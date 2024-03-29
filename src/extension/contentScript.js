alert("Script Running");

// chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
//     if (message.action === 'generate') {
//         generateSummary(sendResponse);
//         // sendResponse()
//     }
// });

chrome.runtime.onConnect.addListener(function (port) {
  console.assert(port.name == "popup-content");


port.onMessage.addListener(function (message) {
  if (message.action == "generate") {
    const currentTabUrl = window.location.href;

    const url =
      "http://localhost:5000/api/summarize?youtube_url=" +
      encodeURIComponent(currentTabUrl);
    const response = fetch(url, {
      method: "get",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        // console.log(response.json())
        return response.json();
      })
      .then((data) => {
        console.log(data);
        port.postMessage({ data: data });
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  }
});

});

// function generateSummary(sendResponse) {
//   const currentTabUrl = window.location.href;

//   const url =
//     "http://localhost:5000/api/summarize?youtube_url=" +
//     encodeURIComponent(currentTabUrl);
//   const response = fetch(url, {
//     method: "get",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   })
//     .then((response) => {
//       if (!response.ok) {
//         throw new Error("Network response was not ok");
//       }
//       // console.log(response.json())
//       return response.json();
//     })
//     .then((data) => {
//       console.log(data);
//       sendResponse({ response: data });
//     })
//     .catch((error) => {
//       console.error("There was a problem with the fetch operation:", error);
//     });
// }
