/* global document, window, sessionStorage, fetch */

const frm = document.getElementById('red-flag-form');
const token = sessionStorage.getItem('token');
const info = document.getElementById('info-messages');

// Image handler
function fileHandler(type, incidentId) {
  const url = `http://127.0.0.1:5000/${type}/${incidentId}`;
  // eslint-disable-next-line no-undef
  const formData = new FormData();
  let input = '';
  if (type === 'addimage') {
    input = document.querySelector('#upload-image');
  } else {
    input = document.querySelector('#upload-video');
  }

  formData.append('file', input.files[0]);

  if (input.files[0] !== undefined) {
    fetch(url, {
      method: 'POST',
      mode: 'cors',
      body: formData,
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(response => response.json())
      .then((data) => {
        if (data.status === 200) {
          // eslint-disable-next-line no-console
          console.log(data);
        } else {
          info.parentElement.style.display = 'block';
          info.textContent = `${data.error}`;
        }
      });
  }
}

// eslint-disable-next-line no-unused-vars
function createRedflag(event) {
  event.preventDefault();
  const title = document.getElementById('title');
  const location = document.getElementById('location');
  const comment = document.getElementById('comment');
  const url = 'http://127.0.0.1:5000/api/v2/red-flags';

  fetch(url, {
    method: 'POST',
    mode: 'cors',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      title: title.value,
      location: location.value,
      comment: comment.value,
    }),
  })
    .then(response => response.json())
    // eslint-disable-next-line consistent-return
    .then((data) => {
      if (data.status === 401) {
        window.location.replace('./signin.html');
      }
      if (data.status === 201) {
        info.parentElement.style.display = 'block';
        info.textContent = `${data.data[0].message}`;
        // eslint-disable-next-line prefer-destructuring
        const id = data.data[0].id;
        fileHandler('addimage', id);
        fileHandler('addvideo', id);
        frm.reset();
        return false;
      }
      info.parentElement.style.display = 'block';
      info.textContent = `${data.error}`;
    })
    // eslint-disable-next-line no-console
    .catch(err => console.log(err), info.textContent = 'An unknown error has occured! Please try again.');
}


// imageHandler();
frm.addEventListener('submit', createRedflag);
// frm.addEventListener('submit', (createRedflag, imageHandler));
