console.log("workerscript 1");

function onTextParsedListener(textParsedDetails) {
    sendMessageToCaller("page-content",
        textParsedDetails,
        textParsedDetails.url,
        textParsedDetails.pageId
    );
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

/**
 * Handle events from the main thread
 *
 * @param {MessageEvent} event - message
 * @param {MessageEvent.data} event.data - initialization data
 * @listens MessageEvent
 */
self.addEventListener("message", event => {
    console.info("Got event from main thread: ");
    console.info(event);
    if ((typeof event.data === "object") &&
        ("eventName" in event.data) &&
        (event.data.eventName === "webScience.pageText.onTextParsed")) {
        onTextParsedListener.apply(null, event.data.listenerArguments);
    }
    else if (typeof event.data === "object" &&
        "type" in event.data &&
        event.data.type === "init") {
        initialize(event.data);
    }
});

function initialize(initializationData){
    console.log("Initialized worker.");
}

/**
 * Error handler
 * @param {ErrorEvent} event - error object
 * @listens ErrorEvent
 */
onerror = event => {
    console.error("error:", event.message);
}

