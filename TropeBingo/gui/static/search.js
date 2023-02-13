window.onload = function() {
  var searchInput = document.getElementById("search-input");

  var searchResults = document.getElementById("search-results");

  searchInput.addEventListener("input", function () {
    var query = searchInput.value;
    // Perform an AJAX request to the server
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/search?q=" + encodeURIComponent(query), true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          // Update the search results
          searchResults.innerHTML = xhr.responseText;
        } else {
          // Handle error
          searchResults.innerHTML = "An error occurred.";
        }
      }
    };
    xhr.send();
  });
}