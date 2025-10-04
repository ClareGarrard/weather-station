// Uses a mixture of new functions with old syntax to support both modern and legacy browsers.
// Legacy support is specifically tailored to Firefox Version 5.3 (2) for iOS.

var DATA_UPDATE_INTERVAL_SECONDS = 60;

function updateData() {
    if (window.fetch) {
        // Modern browsers: use fetch API
        fetch("/api/data")
            .then(function(response) { return response.json(); })
            .then(function(data) { updateFeatures(data); })
            .catch(console.error);
    } else {
        // Legacy browsers: use XMLHttpRequest
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/api/data", true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        var data = JSON.parse(xhr.responseText);
                        updateFeatures(data);
                    } catch (e) {
                        console.error(e);
                    }
                } else {
                    console.error("XHR error: " + xhr.status);
                }
            }
        };
        xhr.send();
    }
}

function updateFeatures(data) {
    // find all feature-value elements
    var features = document.querySelectorAll('[data-key]');
    // extract keyword from data attribute
    var keywords = [];
    for (var i = 0; i < features.length; i++) {
        keywords.push(features[i].dataset.key);
    }

    // iterate through each feature-keyword pair
    for (var idx = 0; idx < keywords.length; idx++) {
        var feature = features[idx];
        var keyword = keywords[idx];
        var dataValue = data[keyword];

        // set the value of the html element to the value of the data
        feature.textContent = dataValue;
    }
}

setInterval(updateData, DATA_UPDATE_INTERVAL_SECONDS * 1000);
