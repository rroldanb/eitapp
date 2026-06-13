(function() {
  var pasteArea = document.getElementById('paste-area');
  if (!pasteArea) return;

  pasteArea.addEventListener('paste', async function(event) {
    var items = event.clipboardData.items;
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        var file = items[i].getAsFile();
        var reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById('preview').src = e.target.result;
          document.getElementById('preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
        var base64 = await toBase64(file);
        document.getElementById('image_file').value = base64;
      }
    }
  });

  function toBase64(file) {
    return new Promise(function(resolve, reject) {
      var reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = function() { resolve(reader.result); };
      reader.onerror = function(error) { reject(error); };
    });
  }
})();
