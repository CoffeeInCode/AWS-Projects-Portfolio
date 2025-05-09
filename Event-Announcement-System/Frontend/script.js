// IMPORTANT: Replace with your actual API Gateway Invoke URL
const API_GATEWAY_INVOKE_URL = 'https://yc3129tqy6.execute-api.us-west-2.amazonaws.com/prod'; // e.g., https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod
const EVENTS_FILE_URL = './events.json'; // Or the full S3 public URL if preferred and configured for CORS

document.addEventListener('DOMContentLoaded', () => {
    loadEvents();
    setupForms();
});

async function loadEvents() {
    const eventListDiv = document.getElementById('eventList');
    eventListDiv.innerHTML = '<p>Loading events...</p>';
    try {
        // Add a cache-busting query parameter
        const response = await fetch(`${EVENTS_FILE_URL}?t=${new Date().getTime()}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const events = await response.json();

        if (events.length === 0) {
            eventListDiv.innerHTML = '<p>No upcoming events.</p>';
            return;
        }

        eventListDiv.innerHTML = ''; // Clear loading message
        events.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.classList.add('event-item');
            eventElement.innerHTML = `
                <h3>${escapeHTML(event.title)}</h3>
                <p><strong>Date:</strong> ${escapeHTML(event.date)}</p>
                <p><strong>Description:</strong> ${escapeHTML(event.description)}</p>
            `;
            eventListDiv.appendChild(eventElement);
        });
    } catch (error) {
        console.error('Error loading events:', error);
        eventListDiv.innerHTML = '<p>Could not load events. Please try again later.</p>';
    }
}

function setupForms() {
    const subscribeForm = document.getElementById('subscribeForm');
    const createEventForm = document.getElementById('createEventForm');
    const subscribeMessageEl = document.getElementById('subscribeMessage');
    const createEventMessageEl = document.getElementById('createEventMessage');

    subscribeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const email = document.getElementById('email').value;
        subscribeMessageEl.textContent = 'Subscribing...';

        if (!validateEmail(email)) {
            subscribeMessageEl.textContent = 'Invalid email address.';
            subscribeMessageEl.style.color = 'red';
            return;
        }

        try {
            const response = await fetch(`${API_GATEWAY_INVOKE_URL}/subscribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email }),
            });
            const result = await response.json();
            if (response.ok) {
                subscribeMessageEl.textContent = result.message || 'Subscription request sent! Check your email to confirm.';
                subscribeMessageEl.style.color = 'green';
                document.getElementById('email').value = ''; // Clear input
            } else {
                throw new Error(result.message || 'Subscription failed.');
            }
        } catch (error) {
            console.error('Subscription error:', error);
            subscribeMessageEl.textContent = `Error: ${error.message}`;
            subscribeMessageEl.style.color = 'red';
        }
    });

    createEventForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const title = document.getElementById('eventTitle').value;
        const date = document.getElementById('eventDate').value;
        const description = document.getElementById('eventDescription').value;
        createEventMessageEl.textContent = 'Creating event...';

        try {
            const response = await fetch(`${API_GATEWAY_INVOKE_URL}/create-event`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, date, description }),
            });
            const result = await response.json();
             if (response.ok) {
                createEventMessageEl.textContent = result.message || 'Event created successfully!';
                createEventMessageEl.style.color = 'green';
                createEventForm.reset(); // Clear form
                loadEvents(); // Refresh the event list immediately
            } else {
                throw new Error(result.message || 'Failed to create event.');
            }
        } catch (error) {
            console.error('Create event error:', error);
            createEventMessageEl.textContent = `Error: ${error.message}`;
            createEventMessageEl.style.color = 'red';
        }
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
      tag => ({
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          "'": '&#39;',
          '"': '&quot;'
        }[tag] || tag)
    );
}