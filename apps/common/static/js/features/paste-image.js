(function () {
  const pasteArea = document.getElementById('paste-area');
  if (!pasteArea) return;

  pasteArea.addEventListener('paste', async function (event) {
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        const reader = new FileReader();
        reader.onload = function (e) {
          document.getElementById('preview').src = e.target.result;
          document.getElementById('preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
        const base64 = await toBase64(file);
        document.getElementById('image_file').value = base64;
      }
    }
  });

  function toBase64(file) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = function () {
        resolve(reader.result);
      };
      reader.onerror = function (error) {
        reject(error);
      };
    });
  }
})();
