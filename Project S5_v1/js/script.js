document.addEventListener('DOMContentLoaded', () => {
    // Highlight the active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        if (window.location.pathname.includes(item.getAttribute('href'))) {
            item.classList.add('active');
        }
    });

    // Logout functionality
    document.addEventListener('DOMContentLoaded', () => {
        const logoutButton = document.getElementById('logout-btn');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => { 
                // Clear session or local storage
                sessionStorage.clear(); // or localStorage.clear();
    
                // Optional: If your backend needs to clear server-side sessions
                fetch('/logout', {
                    method: 'POST',
                    credentials: 'same-origin', // Include cookies in the request
                })
                    .then(response => {
                        if (response.ok) {
                            // Redirect to login page
                            window.location.href = 'login.html';
                        } else {
                            alert('Error logging out. Please try again.');
                        }
                    })
                    .catch(error => {
                        console.error('Error logging out:', error);
                        alert('Error logging out. Please check your connection.');
                    });
            });
        }
    });
    


    // Profile: Edit and Save
    const editProfile = () => {
        document.getElementById('editButton').style.display = 'none';
        document.getElementById('editFields').style.display = 'block';
    };
    const saveProfile = () => {
        const newName = document.getElementById('nameInput').value;
        document.getElementById('name').textContent = newName;
        document.getElementById('editButton').style.display = 'inline';
        document.getElementById('editFields').style.display = 'none';
    };

    // Fetch and Update Profile
    const fetchProfile = () => {
        fetch('http://127.0.0.1:5000/api/profile')
            .then(response => response.json())
            .then(data => {
                document.getElementById('profile-name').textContent = `${data.name} ${data.surname}`;
                document.getElementById('profile-email').textContent = data.email;
                document.getElementById('profile-phone').textContent = data.phone;
                document.getElementById('profile-qualifications').textContent = data.qualifications;
                document.getElementById('profile-specialties').textContent = data.specialties;
                document.getElementById('profile-work-history').textContent = data.work_history;
            })
            .catch(error => console.error('Error fetching profile:', error));
    };

    // Add Card Functionality
    const savedCards = [];
    const addCard = () => {
        document.getElementById('card-input-section').style.display = 'block';
    };
    const saveCard = () => {
        const cardNumber = document.getElementById('card-number').value.trim();
        const cardName = document.getElementById('card-name').value.trim();
        const cardCVV = document.getElementById('card-cvv').value.trim();
        const cardExpiration = document.getElementById('card-expiration').value.trim();

        if (!/^\d{16}$/.test(cardNumber) || !/^[a-zA-Z\s]+$/.test(cardName) ||
            !/^\d{3}$/.test(cardCVV) || !/^\d{2}\/\d{2}$/.test(cardExpiration)) {
            alert("Invalid card details.");
            return;
        }

        savedCards.push({ number: cardNumber, name: cardName, cvv: cardCVV, expiration: cardExpiration });
        alert("Card saved successfully!");
        document.getElementById('card-input-section').style.display = 'none';
        updateManageCardsList();
    };
    const updateManageCardsList = () => {
        const cardList = document.getElementById('card-list');
        cardList.innerHTML = '';
        savedCards.forEach((card, index) => {
            const cardContainer = document.createElement('div');
            cardContainer.className = 'card-item';
            cardContainer.innerHTML = `
                <p>${card.name} - ${card.number} (Exp: ${card.expiration})</p>
                <button onclick="removeCard(${index})">Remove</button>
            `;
            cardList.appendChild(cardContainer);
        });
    };

    // Appointments
    const fetchAppointments = () => {
        fetch('/api/appointments')
            .then(response => response.json())
            .then(data => {
                const appointmentsList = document.getElementById('appointmentsList');
                appointmentsList.innerHTML = '';
                if (data.appointments && data.appointments.length > 0) {
                    data.appointments.forEach(appointment => {
                        const li = document.createElement('li');
                        li.textContent = `${appointment.date} - ${appointment.patientName}`;
                        const deleteBtn = document.createElement('button');
                        deleteBtn.textContent = 'Delete';
                        deleteBtn.onclick = () => deleteAppointment(appointment.id);
                        li.appendChild(deleteBtn);
                        appointmentsList.appendChild(li);
                    });
                } else {
                    appointmentsList.innerHTML = '<li>No appointments available.</li>';
                }
            })
            .catch(error => console.error('Error:', error));
    };

    // Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', event => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            if (email === "user@example.com" && password === "password123") {
                window.location.href = "home.html";
            } else {
                alert("Invalid username or password.");
            }
        });
    }

    // Registration
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', event => {
            event.preventDefault();
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                name: document.getElementById('name').value,
                surname: document.getElementById('surname').value,
                birthdate: document.getElementById('birthdate').value,
                education: document.getElementById('education').value,
                experience: document.getElementById('experience').value
            };
            console.log("Registration data:", formData);
            window.location.href = "verify.html";
        });
    }
});
// Injecting Footer from footer.html into the footer placeholder
document.getElementById("footer").innerHTML = `
    <link rel="stylesheet" href="footer.css">
    <footer>
        <p>HealMount - All Rights Reserved</p>
        <p><a href="contact.html">Contact Support</a> | <a href="faq.html">FAQs</a></p>
    </footer>
`;
