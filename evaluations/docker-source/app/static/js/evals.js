function calcEvals(method) {
  // let rW = document.querySelector(".resultsWrapper");
  let uInfo = document.querySelector("#user_info_"+method);
  uInfo.innerHTML = "Please wait...";
  fetch('/calc/' + method)
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((myJson) => {
      // results
      let resultsHtml = "";
      let userInfoHtml = "";
      if (myJson.success) {
        // let all_plots = createImageLinksFromArray(myJson.message.plots);
        // let selected_plots = createImageLinksFromArray(myJson.message.plots.filter(path => path.includes('box') && path.includes('VIDEO_TOOL')));
        // selected_plots += createImageLinksFromArray(myJson.message.plots.filter(path => path.includes('scatter')));

        // resultsHtml = "<h4>Visual Analysis</h4>" +
        //               "<p>Plots visualizing time efficiency and annotation accuracy.</p>" +
        //               "<div class='result_row'>" +
        //               "<fieldset><legend>plots(time, accuracy)</legend>" +
        //               "<div class='plots'>"+selected_plots+"</div>" +
        //               "</fieldset>" +
        //               "</div>" +
        //               "<h4>Correlations</h4>" +
        //               "<p>Annotation (IoU) accuracy-time correlation using Spearmans Rank Correlation Coefficient by tool, video and both.</p>" +
        //               "<div class='result_row'>" +
        //               "<fieldset><legend>Spearman</legend>" +
        //               myJson.message.corr +
        //               "</fieldset>" +
        //               "</div>";

        // redirect to load successfully created data
        // location.href='/evals';
        window.location.replace("/evals");
        // userInfoHtml = "<span class='success'>Success.</span>";
      }
      else {
        resultsHtml = "Not Available."
        userInfoHtml = "<span class='error'>Errors occurred. See Console for details.</span>";
        // rW.innerHTML = resultsHtml;
        uInfo.innerHTML = userInfoHtml;
        // user info
        console.log("Fetch response:");
        // console.log(JSON.stringify(myJson));
        console.log(myJson);
      }

    })
    .catch(error => {
      console.error('Error:', error);
      userInfoHtml = "<span class='error'>Errors occurred. See Console for details.</span>";
      uInfo.innerHTML = userInfoHtml;
    });
}
