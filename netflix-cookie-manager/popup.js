document.addEventListener('DOMContentLoaded', function() {
  loadCookies();

  document.getElementById('addCookieBtn').addEventListener('click', addCookie);
  document.getElementById('launchBtn').addEventListener('click', launchNetflix);
});

function loadCookies() {
  chrome.storage.local.get(['netflixCookies'], function(result) {
    const cookies = result.netflixCookies || [];
    displayCookies(cookies);
  });
}

function saveCookies(cookies) {
  chrome.storage.local.set({ netflixCookies: cookies }, function() {
    loadCookies();
  });
}

function displayCookies(cookies) {
  const list = document.getElementById('cookieList');
  list.innerHTML = '';

  cookies.forEach((cookie, index) => {
    const li = document.createElement('li');
    li.textContent = `${cookie.name}`;

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'X';
    deleteBtn.className = 'delete-btn';
    deleteBtn.onclick = () => deleteCookie(index);

    li.appendChild(deleteBtn);
    list.appendChild(li);
  });
}

function deleteCookie(index) {
  chrome.storage.local.get(['netflixCookies'], function(result) {
    const cookies = result.netflixCookies || [];
    const cookieToRemove = cookies[index];

    if (cookieToRemove) {
      chrome.cookies.remove({
        url: 'https://www.netflix.com',
        name: cookieToRemove.name
      }, function(details) {
        if (chrome.runtime.lastError) {
           console.error("Error removing cookie from browser:", chrome.runtime.lastError);
        } else {
           console.log("Cookie removed from browser:", details);
        }
      });
    }

    cookies.splice(index, 1);
    saveCookies(cookies);
    setStatus('Cookie deleted.', 'success');
  });
}

function addCookie() {
  const nameInput = document.getElementById('cookieName');
  const valueInput = document.getElementById('cookieValue');
  const name = nameInput.value.trim();
  const value = valueInput.value.trim();

  if (!name || !value) {
    setStatus('Please enter both name and value.', 'error');
    return;
  }

  const newCookie = {
    url: 'https://www.netflix.com',
    name: name,
    value: value,
    domain: '.netflix.com',
    path: '/',
    secure: true,
    sameSite: 'no_restriction'
  };

  // Set the cookie in the browser
  chrome.cookies.set(newCookie, function(cookie) {
    if (cookie) {
      // Save to storage for persistence
      chrome.storage.local.get(['netflixCookies'], function(result) {
        const cookies = result.netflixCookies || [];
        // Check if cookie with same name exists, update if so
        const existingIndex = cookies.findIndex(c => c.name === name);
        if (existingIndex >= 0) {
            cookies[existingIndex] = newCookie;
        } else {
            cookies.push(newCookie);
        }

        saveCookies(cookies);
        setStatus(`Cookie ${name} set successfully.`, 'success');
        nameInput.value = '';
        valueInput.value = '';
      });
    } else {
      setStatus('Failed to set cookie. Check permissions or values.', 'error');
      if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError);
      }
    }
  });
}

function launchNetflix() {
  chrome.tabs.create({ url: 'https://www.netflix.com' });
}

function setStatus(message, type) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = 'status ' + type;
  setTimeout(() => {
    status.textContent = '';
    status.className = 'status';
  }, 3000);
}
