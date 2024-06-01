const chatIcon = document.querySelector("#chatIcon");
const chatContainer = document.querySelector("#chat-container");

// Function to slide the container in
// Function to slide the container out

 function isContainerVisible() {
     const style = window.getComputedStyle(chatContainer);
     return style.getPropertyValue('transform') === 'matrix(1, 0, 0, 1, 0, 0)'; // Check if the container is fully visible
 }
 function slideOutContainer() {
     chatContainer.style.transform = "translateX(100%)"; // Slide the container off-screen
     chatContainer.addEventListener("transitionend", () => {
         chatContainer.style.display = "none 0.3s ease"; // Hide the container after the slide-out animation
         chatIcon.innerHTML = '<i class="fas fa-comment"></i>';
     }, { once: true }); // Remove the event listener after it's used once
 }

 // Function to slide the container in
 function slideInContainer() {
     chatContainer.style.display = "block"; // Show the container
     chatContainer.style.transform = "translateX(100%)"; // Move the container off-screen initially
     setTimeout(() => {
         chatContainer.style.transform = "translateX(0)"; // Slide the container into view
     }, 20);
 }

 chatIcon.addEventListener("click", () => {
     if (!isContainerVisible()) {
         slideInContainer(); // Slide the container in if it's not visible
         chatIcon.innerHTML = '<i class="fas fa-times"></i>';
     } else {
         slideOutContainer(); // Slide the container out if it's already visible
     }
 });



     // Add transitionend event listener to handle smooth display and hiding of the chat container
 // chatContainer.addEventListener("transitionend", () => {
 //     if (chatContainer.style.display === "block") {
 //         chatContainer.style.opacity = "1"; // Set opacity to 1 after sliding in
 //     } else {
 //         chatContainer.style.display = "none"; // Hide the container after sliding out
 //     }
 // });

 function scrollToBottom() {
         const chatBox = document.querySelector(".chat-box");
         chatBox.scrollTop = chatBox.scrollHeight;
     }

 function scrollToLowerPosition() {
     const chatBox = document.querySelector(".chat-box");
     const containerDivHeight = document.querySelector("#container-div").offsetHeight;
     const offset = 20; // Adjust the offset as needed
     chatBox.scrollTop = containerDivHeight + offset;
 }

 // Add event listener to submit form asynchronously
 const form = document.querySelector("#user-input-form");

 form.addEventListener("submit", async(e) => {
     e.preventDefault(); // Prevent the default form submission behavior
     const formData = new FormData(form);
     const userMessage = formData.get("user_input");

     // Get the CSRF token from the cookie
     const csrftoken = getCookie("csrftoken");

     // Display user message in the chat box
     const userMessageDiv = document.createElement("div");
     userMessageDiv.classList.add("mt-3", "p-3", "rounded", "user-message", );
     userMessageDiv.innerHTML = `<p>${userMessage}</p>`;
     document.querySelector(".chat-box").appendChild(userMessageDiv);

     try {
         console.log("Sending request...");
         const response = await fetch("/", {
             method: "POST",
             headers: {
                 "Content-Type": "application/x-www-form-urlencoded",
                 "X-CSRFToken": csrftoken // Include the CSRF token in the headers
             },
             body: new URLSearchParams({
                 user_input: userMessage
             })
         });

         // Check if the response was successful (status code in the range 200-299)
         if (response.ok) {
             console.log("Request successful");
             const data = await response.json();
             console.log("Response data:", data);
             const messageDiv = document.createElement("div");
             messageDiv.classList.add("mt-3", "p-3", "rounded", "bot-message");
             messageDiv.innerHTML = `<p>${data.response}</p>`;
             document.querySelector(".chat-box").appendChild(messageDiv);
             // Add slide-in animation only to bot messages
             messageDiv.classList.add("slide-in");
             scrollToBottom();
         } else {
             // Handle server-side errors or other non-successful responses
             console.error("Server responded with an error:", response.statusText);
         }
     } catch (error) {
         // Handle any other errors that might occur during the fetch
         console.error("Error during fetch:", error);
     }

     // Clear the input box after submitting the message
     document.querySelector("#user-input").value = "";
 });

 // Function to get CSRF token from cookie
 function getCookie(name) {
     let cookieValue = null;
     if (document.cookie && document.cookie !== '') {
         const cookies = document.cookie.split(';');
         for (let i = 0; i < cookies.length; i++) {
             const cookie = cookies[i].trim();
             // Does this cookie string begin with the name we want?
             if (cookie.substring(0, name.length + 1) === (name + '=')) {
                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
             }
         }
     }
     return cookieValue;
 }

 document.addEventListener("DOMContentLoaded", () => {
     // Sample pre-existing answers
     const preExistingAnswers = [
         "Hello! I'm Jazz. How can I assist you today?",
        
     ];

     // Add pre-existing answers to the chatbox with animation
     const chatBox = document.querySelector(".chat-box");
     preExistingAnswers.forEach((answer, index) => {
         setTimeout(() => {
             const botMessageDiv = document.createElement("div");
             botMessageDiv.classList.add("mt-3", "p-3", "rounded", "bot-message");
             botMessageDiv.innerHTML = `<p>${answer}</p>`;
             chatBox.appendChild(botMessageDiv);
             // Only apply slide-in animation to bot messages
             botMessageDiv.classList.add("slide-in");
             scrollToBottom();
         }, index * 1000); // Add a delay between each message for a staggered effect
     });
 });



 async function createZendeskTicket(userMessage) {
     const zendeskEndpoint = 'https://universitikebangsaanmalaysia.zendesk.com/api/v2/tickets.json';
     const zendeskAPIToken = 'Lb95qIwuEPI5JDQ80zWjK2AMvYWJxkX6pIlveoC0'; // Replace with your Zendesk API token
     const zendeskEmail = 'mifzalmaf@gmail.com'; // Replace with your Zendesk account email

     const requestBody = new URLSearchParams({
         'ticket[subject]': 'Support Request',
         'ticket[description]': userMessage
     });

     try {
         const response = await fetch(zendeskEndpoint, {
             method: 'POST',
             headers: {
                 'Authorization': `Basic ${btoa(`${zendeskEmail}/token:${zendeskAPIToken}`)}`,
                 'Content-Type': 'application/x-www-form-urlencoded'
             },
             body: requestBody
         });

         if (response.ok) {
             const data = await response.json();
             console.log('Ticket created successfully:', data);
             return data;
         } else {
             throw new Error('Failed to create ticket: ' + response.statusText);
         }
     } catch (error) {
         console.error('Error creating ticket:', error);
         throw error;
     }
 }

 // Example usage:
 const userMessage = 'Support';
 const requesterEmail = 'example@example.com'; // Replace with the email of the requester
 createZendeskTicket(userMessage, requesterEmail);

 // Function to handle form submission
 async function handleSubmit(event) {
     event.preventDefault(); // Prevent form submission
     const userMessage = document.getElementById('user-input').value; // Get user message from input field

     try {
         // Create Zendesk ticket with user message
         const ticketData = await createZendeskTicket(userMessage);
         console.log('Ticket created:', ticketData);

         // Optionally, display a success message or perform other actions
         alert('Support ticket created successfully!');
     } catch (error) {
         // Handle errors
         console.error('Error creating ticket:', error);
         alert('Failed to create support ticket. Please try again later.');
     }
 }

 // Add event listener to form submission
 document.getElementById('user-input-form').addEventListener('submit', handleSubmit);

 async function handleUserInput(userMessage) {
 // Check if the user message contains the trigger word
 const triggerWords = ["help", "support", "assistance", "question", "issue", "problem", "technical support", "customer service"];
 const containsTriggerWord = triggerWords.some(word => userMessage.toLowerCase().includes(word));

 if (containsTriggerWord) {
     // If the trigger word is detected, create a support ticket in Zendesk
     try {
         const ticketResponse = await createZendeskTicket(userMessage);
         // Respond to the user indicating that their request has been received
         displayBotMessage("Your request has been received. We'll get back to you shortly.");
     } catch (error) {
         // Handle any errors that occur during ticket creation
         console.error('Error creating support ticket:', error);
         displayBotMessage("Sorry, we encountered an error while processing your request. Please try again later.");
     }
 } else {
     // If no trigger word is detected, continue with regular chatbot responses
     // Call a function to handle other types of user messages
     handleRegularUserMessage(userMessage);
 }
}

// Function to fetch ticket comments (admin responses) from Zendesk
async function fetchTicketComments(ticketId) {
 const zendeskEndpoint = 'https://universitikebangsaanmalaysia.zendesk.com/api/v2/tickets.json';
 const zendeskAPIToken = 'Lb95qIwuEPI5JDQ80zWjK2AMvYWJxkX6pIlveoC0'; // Replace with your Zendesk API token
 const zendeskEmail = 'mifzalmaf@gmail.com';;

 try {
     const response = await fetch(zendeskEndpoint, {
         headers: {
             'Authorization': `Basic ${btoa(`${zendeskEmail}/token:${zendeskAPIToken}`)}`
         }
     });

     if (response.ok) {
         const data = await response.json();
         // Process the response data (ticket comments) and display admin responses in the chat interface
         console.log('Ticket comments:', data.comments);
     } else {
         throw new Error('Failed to fetch ticket comments');
     }
 } catch (error) {
     console.error('Error fetching ticket comments:', error);
 }
}

// Example usage: Fetch comments for a specific ticket (replace '123' with the actual ticket ID)
fetchTicketComments(123);

