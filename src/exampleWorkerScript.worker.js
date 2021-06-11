console.debug("Running worker script");

function onTextParsedListener(textParsedDetails) {
    sendMessageToCaller("text-scraper",
        textParsedDetails,
        textParsedDetails.url,
        textParsedDetails.pageId
    );
}

/**
 * Handle events from the main thread
 *
 * @param {MessageEvent} event - message
 * @param {MessageEvent.data} event.data - initialization data
 * @listens MessageEvent
 */
self.addEventListener("message", event => {
    if ((typeof event.data === "object") &&
        ("eventName" in event.data) &&
        (event.data.eventName === "webScience.pageText.onTextParsed")) {
        onTextParsedListener.apply(null, event.data.listenerArguments);
    }
});

/**
 * Error handler
 * @param {ErrorEvent} event - error object
 * @listens ErrorEvent
 */
onerror = event => {
    console.error("error:", event.message);
}

/**
 * Send a message to the main thread that spawned this worker thread
 * Each message has a type property for the main thread to handle messages.
 * The data property in the message contains the data object that the worker
 * thread intends to send to the main thread.
 *
 * @param {string} workerId - ID of this worker.
 * @param {number} data - Url, text, and content.
 * @param {string} url - URL of the page.
 * @param {string} pageId - WebScience pageId assigned to the page.
 */
function sendMessageToCaller(workerId, data, url, pageId) {
    postMessage({
        type: workerId,
        url: url,
        data: data,
        pageId: pageId
    });
}
