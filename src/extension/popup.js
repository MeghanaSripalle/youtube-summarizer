document.addEventListener("DOMContentLoaded", function() {

document.getElementById('summarizeBtn').addEventListener('click', async function() {
    console.log("sum")
   
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const activeTab = tabs[0];
    var port = await chrome.tabs.connect(activeTab.id, {name: "popup-content"});
    port.postMessage({action:"generate"})

    port.onMessage.addListener(function(msg) {
        
        if (msg.data) {
          
          console.log("Data received from content script:", msg.data);
          outputSummary(msg.data)
        } else if (msg.error) {
          console.error("Error received from content script:", msg.error);
        }
    
    })
    });
});



function outputSummary(summary) {
    document.getElementById('summaryContainer').innerText = summary;
}


