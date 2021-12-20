const API_URI = 'https://tes7ayyf28.execute-api.us-east-1.amazonaws.com/v0/url-shortener';

let shortenUrl = (originalUrl) => {
    if (!originalUrl || !originalUrl.trim()) {
        return;
    }
    const data = {originalUrl: `${originalUrl}`}
    fetch(API_URI, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(body => {
        const url = body.body;
        const htmlElement = document.getElementById('shortenedUrl');
        htmlElement.innerHTML = `The shortened url is: <a href=\"${url}\">${url}</a>`;
    })
    .catch(err => window.alert(err));
}