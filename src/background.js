import { pageText, workers } from "@mozilla/web-science";

const worker = new Worker("/dist/pageContentsWorkerScript.worker.js");
const name = 'page-contents';
const matchPatterns = ["<all_urls>"];

worker.postMessage({
  type: "init",
  name: name,
  args: null
});

worker.onmessage = event => {
  savePageContents(event.data);
};

pageText.onTextParsed.addListener(
  workers.createEventListener(worker),
  {
    matchPatterns: matchPatterns
  }
);

// Callback for worker
function savePageContents(result) {
  console.log("Page text retrieved.");
  const message = [result.url, result.data.title, result.data.textContent].join("&&&&&")
  var sending = browser.runtime.sendNativeMessage(
    "savePageData",
    JSON.stringify(message));
  sending.then(onResponse, onError);
}

function onResponse(response) {
  console.log("Received " + response);
}

function onError(error) {
  console.log(`Error: ${error}`);
}
