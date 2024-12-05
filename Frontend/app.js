let covidChart = null;
let selectedCountries = [];
let startDate = '';
let endDate = '';
let selectedCategory = '';
let selectedCategoryName = '';
let selectedMetric = '';
let selectedMetricName = '';
let selectedPerMillion = false;

const hospitalizationsIndicators = ["Daily hospital occupancy", "Daily ICU occupancy", "Weekly new hospital admissions", "Weekly new ICU admissions"];
const testingMetrics = [["Cumulative Total (CT)", "t_cumulative_total"], ["Daily Change in CT", "t_daily_change_ct"], ["CT Per Thousand", "t_ct_per_thousand"], 
                        ["Daily Change in CT Per Thousand", "t_daily_change_ct_per_thousand"], ["Short Term Positive Rate", "t_short_term_positive_rate"], 
                        ["Short Term Tests Per Case", "t_short_term_tests_per_case"]];
const vaccinationsMetrics = [["Total Vaccinations", "v_total_vaccinations"], ["People Fully Vaccinated", "v_people_fully_vaccinated"], ["Total Boosters", "v_total_boosters"], 
                                ["Daily Vaccinations", "v_daily_vaccinations"], ["Pople Fully Vaccinated Per Hundred", "v_people_fully_vaccinated_per_hundred"], 
                                ["Total Boosters Per Hundred", "v_total_boosters_per_hundred"]];


// Retrieve all valid country names from database
async function populateCountries() 
{
    try 
    {
        const response = await fetch('http://127.0.0.1:5000/api/get-countries');
        if (!response.ok) 
        {
            throw new Error(`${response.status} ${response.statusText}`);
        }

        const countries = await response.json();
        console.log(countries);

        const countrySelect = document.getElementById('country-select');
        countrySelect.innerHTML = '';

        countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countrySelect.appendChild(option);
        });

        initMultiSelect();

    } 
    catch (error) 
    {
        console.error('Error fetching countries: ', error);
    }
}

function updateSelectedCountries(values) 
{
    selectedCountries = values.map(value => value.value)
}

function getSelectedDates() 
{
    startDate = document.getElementById('start-date').value;
    endDate = document.getElementById('end-date').value;
}

function validateInputs()
{
    const startDateInput = document.getElementById('start-date').value;
    const endDateInput = document.getElementById('end-date').value;
    const errorMessage = document.getElementById('date-error');
    const categoryInput = document.getElementById('data-to-view').value;
    const metricInput = document.getElementById('metric-select').value;

    if (selectedCountries.length === 0)
    {
        errorMessage.textContent = 'Please select at least 1 country';
        return false;
    }

    if (!startDateInput || !endDateInput)
    {
        errorMessage.textContent = 'Please select start and end dates';
        return false;
    }

    if (new Date(endDateInput) <= new Date(startDateInput))
    {
        errorMessage.textContent = 'End date must come after selected start date';
        return false;
    }

    if (!categoryInput)
    {
        errorMessage.textContent = 'Please select a data category to view';
        return false;
    }
    else 
    {
        if ((categoryInput === "hospitalizations" || categoryInput === "testing" || categoryInput === "vaccinations") && !metricInput)
        {
            errorMessage.textContent = 'Please select a metric/indicator';
            return false;
        }
    }
    
    errorMessage.textContent = '';
    return true;
}

async function singleCountryQueries()
{
    try
    {
        const params = new URLSearchParams({
            country: selectedCountries[0],
            start: startDate,
            end: endDate
        });

        if (selectedCategory === "testing" || selectedCategory === "vaccinations")
        {
            params.append('metric', selectedMetric);
        }
        else if (selectedCategory === "hospitalizations")
        {
            params.append('indicator', selectedMetric);
            params.append('per_million', selectedPerMillion);
        }
        
        const url = `http://127.0.0.1:5000/api/${selectedCategory}-by-country?${params.toString()}`;

        const response = await fetch(url);

        if (!response.ok)
        {
            const errorData = await response.json();
            const error = new Error(`HTTP request error!: Status: ${response.status}, Message: ${errorData.error}`);
            error.status = response.status;
            throw error;
        }

        const data = await response.json();
        console.log(data);

        return data;
    }
    catch (error)
    {
        console.error(error);
        return error.status;
    }
}

async function multiCountryComparisonQueries()
{
    try
    {
        const params = new URLSearchParams();
        selectedCountries.forEach(country => {
            params.append('countries', country);
        });
        params.append('start', startDate);
        params.append('end', endDate);

        if (selectedCategory === "testing" || selectedCategory === "vaccinations")
        {
            params.append('metric', selectedMetric);
        }
        else if (selectedCategory === "hospitalizations")
        {
            params.append('indicator', selectedMetric);
            params.append('per_million', selectedPerMillion);
        }
        
        const url = `http://127.0.0.1:5000/api/compare-${selectedCategory}-by-country?${params.toString()}`;

        const response = await fetch(url);

        if (!response.ok)
        {
            const errorData = await response.json();
            const error = new Error(`HTTP request error!: Status: ${response.status}, Message: ${errorData.error}`);
            error.status = response.status;
            throw error;
        }

        const data = await response.json();
        console.log(data);

        return data;
    }
    catch (error)
    {
        console.error(error);
        return error.status;
    }
}

// Extract date labels and data points
function parseSingleCountryData(rawData)
{
    const labels = [];
    const data = [];
    let indicator = '';

    rawData.forEach(entry => {
        if (selectedCategory === "cases" || selectedCategory === "deaths" || selectedCategory === "vaccinations")
        {
            labels.push(entry[0]);
            data.push(entry[1]);
        }
        else 
        {
            labels.push(entry[0]);
            indicator = entry[1];
            data.push(entry[2]);
        }
    });

    return { labels, data, indicator };
}

function parseMultiCountryData(rawData)
{
    const labels = [];
    const datasets = [];
    let indicator = '';
    const countries = Object.keys(rawData);

    countries.forEach(country => {
        const countryData = rawData[country];
        const data = [];
        let legendNote = '';

        countryData.forEach(entry => {
            if (selectedCategory === "cases" || selectedCategory === "deaths" || selectedCategory === "vaccinations")
            {
                if (labels.length < countryData.length)
                {
                    labels.push(entry[0]);
                }
                data.push(entry[1]);
            }
            else 
            {
                if (labels.length < countryData.length)
                {
                    labels.push(entry[0]);
                }
                indicator = entry[1];
                data.push(entry[2]);
            }
        });
            
        if (selectedCategory === "cases" || selectedCategory === "deaths")
        {
            legendNote = '';
            indicator =  selectedCategoryName;
        }
        else if (selectedCategory === "testing")
        {
            legendNote = ` (${indicator})`;
            indicator =  selectedMetricName;
        }
        else if (selectedCategory === "vaccinations")
        {
            legendNote = '';
            indicator =  selectedMetricName;
        }

        datasets.push({ 
            label: `${country}${legendNote}`, 
            data: data, 
            borderColor: getRandomColor(), 
            borderWidth: 1 
        });
    });
    
    return { labels, datasets, indicator };
}

function getRandomColor() 
{ 
    const letters = '0123456789ABCDEF'; 
    let color = '#'; 
    for (let i = 0; i < 6; i++)
    {
        color += letters[Math.floor(Math.random() * 16)];
    }
    
    return color; 
}

function createSingleLineChart(labels, data, indicator, legendNote)
{
    const ctx = document.getElementById('covid-chart').getContext('2d');

    if (covidChart)
    {
        covidChart.destroy();
    }

    let tempChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `${selectedCountries[0]}${legendNote}`,
                    data: data,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: `COVID-19 ${selectedCategoryName} In ${selectedCountries[0]}`
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: indicator
                    }
                },
            }
        }
    });

    return tempChart;
}

function createMultiLineChart(labels, datasets, indicator)
{
    const ctx = document.getElementById('covid-chart').getContext('2d');

    if (covidChart)
    {
        covidChart.destroy();
    }

    let tempChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: `COVID-19 ${selectedCategoryName} In ${selectedCountries.join(", ")}`
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: indicator
                    }
                },
            }
        }
    });

    return tempChart;
}

document.getElementById('update-btn').addEventListener('click', async () => {
    getSelectedDates();

    if (validateInputs())
    {
        console.log('\nRequest Sent: ');
        console.log('Selected countries:', selectedCountries);
        console.log('Start Date:', startDate);
        console.log('End Date:', endDate);
        console.log('Selected Category: ', selectedCategory);
        console.log('Selected Metric/Indicator: ', selectedMetric);
        console.log('Per Million: ', selectedPerMillion);

        if (selectedCountries.length === 1)
        {
            const results = await singleCountryQueries();
            if (results === 420)
            {
                document.getElementById('date-error').textContent = 'Empty query return. Try adjusting dates or country selected.';
            }
            else 
            {
                const cleanedData = parseSingleCountryData(results);
                const labels = cleanedData.labels;
                const data = cleanedData.data;
                let indicator = cleanedData.indicator;
                let legendNote = '';

                if (selectedCategory === "cases" || selectedCategory === "deaths")
                {
                    legendNote = '';
                    indicator =  selectedCategoryName;
                }
                else if (selectedCategory === "testing")
                {
                    legendNote = ` (${indicator})`;
                    indicator =  selectedMetricName;
                }
                else if (selectedCategory === "vaccinations")
                {
                    legendNote = '';
                    indicator =  selectedMetricName;
                }

                covidChart = createSingleLineChart(labels, data, indicator, legendNote);
            }
        }
        else 
        {
            const results = await multiCountryComparisonQueries();
            if (results === 420)
            {
                document.getElementById('date-error').textContent = 'Empty query return. Try adjusting dates or countries selected.';
            }
            else 
            {
                const cleanedData = parseMultiCountryData(results);
                const labels = cleanedData.labels;
                const datasets = cleanedData.datasets;
                let indicator = cleanedData.indicator;

                covidChart = createMultiLineChart(labels, datasets, indicator);
            }
        }
    }
});

document.getElementById('data-to-view').addEventListener('change', () => {
    selectedCategory = document.getElementById('data-to-view').value;
    selectedCategoryName = document.getElementById('data-to-view').options[document.getElementById('data-to-view').selectedIndex].text;
    
    if (document.getElementById('data-to-view').value === "cases" || document.getElementById('data-to-view').value === "deaths")
    {
        document.getElementById('metric-label').style.visibility = 'hidden';
        document.getElementById('metric-select').style.visibility = 'hidden';
        document.getElementById('per-million-label').style.visibility = 'hidden';
        document.getElementById('per-million-cb').style.visibility = 'hidden';
        document.getElementById('per-million-cb').checked = false;
        selectedMetric = '';
        selectedPerMillion = false;
    }
    else 
    {
        document.getElementById('metric-select').innerHTML = '';
        document.getElementById('per-million-label').style.visibility = 'hidden';
        document.getElementById('per-million-cb').style.visibility = 'hidden';
        document.getElementById('per-million-cb').checked = false;
        selectedMetric = '';
        selectedPerMillion = false;

        const placeHolderOption = document.createElement('option');
        placeHolderOption.value = '';
        placeHolderOption.textContent = 'Select a Metric/Indicator';
        placeHolderOption.disabled = true;
        placeHolderOption.selected = true;
        placeHolderOption.hidden = true;

        if (document.getElementById('data-to-view').value === "hospitalizations")
        {
            document.getElementById('metric-select').prepend(placeHolderOption);
            
            hospitalizationsIndicators.forEach(indicator => {
                const option = document.createElement('option');
                option.value = indicator;
                option.textContent = indicator;
                document.getElementById('metric-select').appendChild(option);
            });

            document.getElementById('per-million-label').style.visibility = 'visible';
            document.getElementById('per-million-cb').style.visibility = 'visible';
        }
        else if (document.getElementById('data-to-view').value === "testing")
        {
            document.getElementById('metric-select').prepend(placeHolderOption);
            
            testingMetrics.forEach(metric => {
                const option = document.createElement('option');
                option.value = metric[1];
                option.textContent = metric[0];
                document.getElementById('metric-select').appendChild(option);
            });
        }
        else if (document.getElementById('data-to-view').value === "vaccinations")
        {
            document.getElementById('metric-select').prepend(placeHolderOption);
            
            vaccinationsMetrics.forEach(metric => {
                const option = document.createElement('option');
                option.value = metric[1];
                option.textContent = metric[0];
                document.getElementById('metric-select').appendChild(option);
            });
        }

        document.getElementById('metric-label').style.visibility = 'visible';
        document.getElementById('metric-select').style.visibility = 'visible';
    }
});

document.getElementById('metric-select').addEventListener('change', () => {
    selectedMetric = document.getElementById('metric-select').value;
    selectedMetricName = document.getElementById('metric-select').options[document.getElementById('metric-select').selectedIndex].text;
    console.log(selectedMetric);
});

document.getElementById('per-million-cb').addEventListener('change', () => {
    selectedPerMillion = document.getElementById('per-million-cb').checked;
    console.log(selectedPerMillion);
});

document.addEventListener("DOMContentLoaded", () => {
    populateCountries();
});