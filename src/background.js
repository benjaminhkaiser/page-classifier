import { pageText, workers } from "@mozilla/web-science";

const registeredWorkers = {}

const worker = new Worker("/dist/pageContentsWorkerScript.worker.js");
const name = 'text-scraper';
const listener = savePageText;
const initData = null;
const matchPatterns = ["<all_urls>"];

worker.postMessage({
  type: "init",
  name: name,
  args: initData
});

worker.onmessage = event => {
  listener(event.data);
};

pageText.onTextParsed.addListener(
  workers.createEventListener(worker),
  {
    matchPatterns: matchPatterns
  }
);

registeredWorkers[name] = worker;

// Callback for page-text worker
function savePageText(result) {
  console.log("Page text retrieved.");
  console.log(result.url);
  console.log(result.data.title);
  console.log(result.data.textContent);
}
