
function calcIOU() {
  let rW = document.querySelector(".resultsWrapper");
  let uInfo = document.querySelector(".user_info");
  uInfo.innerHTML = "Please wait...";
  fetch('/calculate_iou')
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((myJson) => {
      // results
      let resultsHtml = "";
      let userInfoHtml = "";
      if (myJson.files && myJson.files.length > 0) {
        for (file of myJson.files) {
          resultsHtml += "<div><a href='" +file+ "' target='_blank'>"+file+"</a></div>\n";
        }
        userInfoHtml = "<span class='success'>Success.</span>";
      }
      else {
        resultsHtml = "Not Available."
        userInfoHtml = "<span class='error'>Errors occurred. See Console for details.</span>";
      }
      rW.innerHTML = resultsHtml;
      uInfo.innerHTML = userInfoHtml;
      // user info
      console.log("Fetch response:");
      // console.log(JSON.stringify(myJson));
      console.log(myJson);
    })
    .catch(error => {
      console.error('Error:', error);
      userInfoHtml = "<span class='error'>Errors occurred. See Console for details.</span>";
      uInfo.innerHTML = userInfoHtml;
    });
}
