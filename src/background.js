import "webextension-polyfill";
import * as webScience from "@mozilla/web-science";

// Contents of eventHandling.js:startSTudy and pageClassification.js go here

/**
 * Registers a worker to run on specified pages and report results back.
 * @param {string} path - Path to file containing the worker to run.
 * @param {MatchPatternSet} matchPatterns - Match patterns for pages on which the worker
 *   should run.
 * @param {string} name - A name for the worker, which can be used to identify which
 *   worker has sent results.
 * @param {Object} initData - Any initialization data that should be sent to the
 *   worker immediately after it starts, before any page content is sent.
 * @param {classificationCallback} listener - Callback to receive classification result.
 */
export function registerWorker(path, matchPatterns, name, initData, listener) {
  const worker = new Worker("/dist/polClassifier.worker.js");
  worker.postMessage({
    type: "init",
    name: "pol-page-classifier",
    args: initData
  });

  worker.onmessage = event => {
    listener(event.data);
  };

  webScience.pageText.onTextParsed.addListener(
    webScience.workers.createEventListener(worker),
    {
      matchPatterns: matchPatterns
    }
  );

  registeredWorkers[name] = worker;
}

pageClassification.registerWorker("/dist/polClassifier.worker.js",
  allDestinationMatchPatterns,
  "page-text",
  polClassifierData,
  saveClassificationResultPol
);

// Example: set a listener for WebScience page navigation events on
// *://*.mozilla.org/* pages. Note that the manifest origin
// permissions currently only include *://*.mozilla.org/*. You should
// update the manifest permissions as needed for your study.
webScience.pageNavigation.onPageData.addListener(pageData => {
  console.log("WebScience page navigation event fired.");
}, {
  matchPatterns: [ "*://*.mozilla.org/*" ]
});

// Example: register a content script for *://*.mozilla.org/* pages
// Note that the content script has the same relative path in dist/
// that it has in src/. The content script can include module
// dependencies (either your own modules or modules from npm), and
// they will be automatically bundled into the content script by
// the build system.
browser.contentScripts.register({
  js: [ { file: "dist/exampleContentScript.content.js" } ],
  matches: [ "*://*.mozilla.org/*" ]
});

// Example: launch a Web Worker, which can handle tasks on another
// thread. Note that the worker script has the same relative path in
// dist/ that it has in src/. The worker script can include module
// dependencies (either your own modules or modules from npm), and
// they will be automatically bundled into the worker script by the
// build system.
new Worker(browser.runtime.getURL("dist/exampleWorkerScript.worker.js"));

// Callback for page-text worker
function savePageText(result) {
  console.log("Page text retrieved.");
  console.log(result.url);
  console.log(result.title);
  console.log(result.body);
}
