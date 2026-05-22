let chartInstance = null;

const API_URL =
    "http://127.0.0.1:8000";

let uploadedDatasets = [];

async function uploadFile() {

    const fileInput =
        document.getElementById("fileInput");

    const file =
        fileInput.files[0];

    if (!file) {

        alert("Please select CSV file");

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    try {

        document.getElementById(
            "uploadStatus"
        ).innerHTML =
            "⏳ Uploading dataset...";

        const response = await fetch(

            `${API_URL}/upload`,

            {
                method: "POST",
                body: formData
            }
        );

        const data =
            await response.json();

        if (data.error) {

            alert(data.error);

            return;
        }

        uploadedDatasets.push(
            file.name
        );

        updateDatasetSelector();

        document.getElementById(
            "uploadStatus"
        ).innerHTML =
            `✅ ${file.name} uploaded successfully`;

        await loadAnalytics();

        await loadColumns();

        await loadInsights();

    } catch (error) {

        console.error(error);

        alert("Upload failed");
    }
}

function updateDatasetSelector() {

    const selector =
        document.getElementById(
            "datasetSelector"
        );

    selector.innerHTML = "";

    uploadedDatasets.forEach(dataset => {

        selector.innerHTML += `
            <option>
                ${dataset}
            </option>
        `;
    });
}


async function loadAnalytics() {

    const response = await fetch(
        `${API_URL}/analytics`
    );

    const data =
        await response.json();

    document.getElementById(
        "rowsKPI"
    ).innerText =
        data.rows;

    document.getElementById(
        "columnsKPI"
    ).innerText =
        data.columns;

    document.getElementById(
        "missingKPI"
    ).innerText =
        data.missing;

    document.getElementById(
        "numericKPI"
    ).innerText =
        data.numeric_count;

    document.getElementById(
        "categoricalKPI"
    ).innerText =
        data.categorical_count;

    document.getElementById(
        "highestKPI"
    ).innerText =
        data.highest_value;

    createChart(
        "bar",
        data.chart_data.labels,
        data.chart_data.values
    );
}


async function loadColumns() {

    const response = await fetch(
        `${API_URL}/columns`
    );

    const data =
        await response.json();

    const xAxis =
        document.getElementById("xAxis");

    const yAxis =
        document.getElementById("yAxis");

    xAxis.innerHTML = "";

    yAxis.innerHTML = "";

    data.categorical.forEach(col => {

        xAxis.innerHTML += `
            <option value="${col}">
                ${col}
            </option>
        `;
    });

    yAxis.innerHTML += `
        <option value="count">
            Count
        </option>
    `;

    data.numeric.forEach(col => {

        yAxis.innerHTML += `
            <option value="${col}">
                ${col}
            </option>
        `;
    });
}


function createChart(
    chartType,
    labels,
    values
) {

    if (chartInstance) {

        chartInstance.destroy();
    }

    const ctx =
        document.getElementById("mainChart");

    chartInstance =
        new Chart(ctx, {

        type: chartType,

        data: {

            labels: labels,

            datasets: [{

                label: "Analytics",

                data: values,

                borderWidth: 2
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false
        }
    });
}


async function updateDynamicChart() {

    const x_col =
        document.getElementById("xAxis").value;

    const y_col =
        document.getElementById("yAxis").value;

    const chart_type =
        document.getElementById("chartType").value;

    const response = await fetch(

        `${API_URL}/dynamic-chart?x_col=${x_col}&y_col=${y_col}&chart_type=${chart_type}`
    );

    const data =
        await response.json();

    createChart(
        chart_type,
        data.labels,
        data.values
    );
}


async function askAI() {

    const questionInput =
        document.getElementById("questionInput");

    const question =
        questionInput.value.trim();

    if (!question) {

        alert("Enter question");

        return;
    }

    const chatBox =
        document.getElementById("chatBox");

    chatBox.innerHTML += `
        <div class="user-message">
            ${question}
        </div>
    `;

    questionInput.value = "";

    chatBox.innerHTML += `
        <div
            class="bot-message"
            id="loadingMessage"
        >
            🤖 AI analyzing...
        </div>
    `;

    const response = await fetch(

        `${API_URL}/ask?question=${encodeURIComponent(question)}`
    );

    const data =
        await response.json();

    document.getElementById(
        "loadingMessage"
    ).remove();

    chatBox.innerHTML += `
        <div class="bot-message">
            🤖 ${data.answer}
        </div>
    `;

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


async function loadInsights() {

    try {

        const response = await fetch(
            `${API_URL}/insights`
        );

        const data =
            await response.json();

        document.getElementById(
            "insightsBox"
        ).innerText =
            data.insights;

    } catch (error) {

        console.error(error);
    }
}


function downloadChart() {

    const canvas =
        document.getElementById("mainChart");

    const link =
        document.createElement("a");

    link.download =
        "analytics_chart.png";

    link.href =
        canvas.toDataURL();

    link.click();
}



function toggleTheme() {

    document.body.classList.toggle(
        "light-mode"
    );
}