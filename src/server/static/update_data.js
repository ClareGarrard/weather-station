const UPDATE_INTERVAL_SECONDS = 60 * 2.5; // 2.5 minutes

function updateData() {
    fetch("/api/data") // request latest data from server
    .then((response) => response.json()) // parse json response
    .then((data) => {
        // find all feature-value elements
        const features = document.querySelectorAll('[data-key]');
        // extract keyword from data attribute
        const keywords = Array.from(features).map(element => element.dataset.key);

        // iterate through each feature-keyword pair
        for (let idx = 0; idx < keywords.length; idx++) {
            const feature = features[idx];
            const keyword = keywords[idx];
            const dataValue = data[keyword];

            // set the value of the html element to the value of the data
            feature.textContent = dataValue;
        }
    })
    .catch(console.error); // log any errors in console
}

setInterval(updateData, UPDATE_INTERVAL_SECONDS * 1000);
