function getPagename(url) {
  var parts = url.split('/');
  return parts.pop() || parts.pop(); // handle potential trailing slash
}

function setMenuHighlight(curPage) {
  let allMenuItems = document.querySelectorAll("#menu li:not(#resetbutton)");
  allMenuItems[0].classList.add("selected"); // select "home by default"
  for (let item of allMenuItems) {
      let page = getPagename(item.firstChild.href)
      if (page === curPage ) {
        allMenuItems[0].classList.remove("selected"); // page found deselect home
        item.classList.add("selected");
      }
  }
}

function createImageLink(imgUrl) {
  imgUrl = imgUrl.replace(/^./, ''); // remove leading dot if exists
  return "<a href='"+imgUrl+"' target='_blank'><fieldset><legend>"+imgUrl+"</legend><img src='"+imgUrl+"'></fieldset></a>";
}
function createImageLinksFromArray(array) {
  let html = "";
  for (url of array) {
    html += createImageLink(url);
  }
  return html;
}

function clearAll() {

  var r = confirm("Clear all evaluation results?");
  if (r !== true) return;
  let curPg = currentPage; // remember caller page

  fetch('/clear')
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((myJson) => {
      // results
      if (myJson.success) {
        // redirect to load successfully created data
        // location.href='/evals';
        window.location.replace("/" + curPg);
      }
      else {
        // user info
        console.log("Fetch response:");
        // console.log(JSON.stringify(myJson));
        console.log(myJson);
      }

    })
    .catch(error => {
      console.error('Error:', error);
      userInfoHtml = "<span class='error'>Errors occurred. See Console for details.</span>";

    });
}

console.log(window.location.href)
let currentPage = getPagename(window.location.href);
setMenuHighlight(currentPage);
