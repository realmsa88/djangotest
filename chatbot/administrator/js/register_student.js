
    // Variable to store selected time slots
    let selectedSlots = [];

    // Function to toggle the selection of a time slot
    function toggleSlotSelection(slot) {
        console.log('Clicked slot:', slot);
        
        // Toggle the 'selected' class for styling
        slot.classList.toggle('selected');

        // Check if the slot is selected
        if (slot.classList.contains('selected')) {
            // Add the slot to selectedSlots if not already included
            if (!selectedSlots.includes(slot.textContent.trim())) {
                selectedSlots.push(slot.textContent.trim());
            }
        } else {
            // Remove the slot from selectedSlots
            const index = selectedSlots.indexOf(slot.textContent.trim());
            if (index !== -1) {
                selectedSlots.splice(index, 1);
            }
        }

        // Log selected time slots for debugging
        console.log('Selected time slots:', selectedSlots);
    }

    // Event listener when DOM content is loaded
    document.addEventListener('DOMContentLoaded', function() {
        let csrftoken = getCSRFToken(); // Retrieve CSRF token
        
        // Function to retrieve CSRF token from cookies
        function getCSRFToken() {
            const name = 'csrftoken';
            const cookieValue = document.cookie.split('; ')
                .find(cookie => cookie.startsWith(name + '='))
                .split('=')[1];
            return cookieValue;
        }

        // Fetch CSRF token once DOM content is loaded
        let modal;

        // Event listener for open modal button
        document.getElementById("openModalBtn").addEventListener("click", function() {
            // Collect student details from form inputs
            const studentName = document.getElementById("id_studentName").value;
            const age = document.getElementById("id_age").value;
            const identificationNumber = document.getElementById("id_identification_number").value;
            const birthdate = document.getElementById("id_birthdate").value;
            const gender = document.getElementById("id_gender").value;
            const race = document.getElementById("id_race").value;
            const teacherName = document.getElementById("id_assigned_teacher").value;
            const parentName = document.getElementById("id_assigned_parent").value;
            const book = document.getElementById("id_book").value;
            const instrument = document.getElementById("id_instrument").value;
            const selectedTimes = selectedSlots.join(", ");
            const selectedDate = document.querySelector('.flatpickr-input').value;

            // Log collected details for debugging
            console.log("Student Details:", {
                studentName, age, identificationNumber, birthdate, gender, race, teacherName, parentName, book, instrument, selectedTimes, selectedDate
            });

            // Populate modal content with student details
            const modalContent = `
                <p>Student Name: ${studentName}</p>
                <p>Age: ${age}</p>
                <p>Identification Number: ${identificationNumber}</p>
                <p>Birth Date: ${birthdate}</p>
                <p>Gender: ${gender}</p>
                <p>Race: ${race}</p>
                <p>Teacher: ${teacherName}</p>
                <p>Parent: ${parentName}</p>
                <p>Book: ${book}</p>
                <p>Instrument: ${instrument}</p>
                <p>Selected Class Times: ${selectedTimes}</p>
                <p>Selected Date: ${selectedDate}</p>
            `;

            // Set modal content
            document.getElementById("modalContent").innerHTML = modalContent;

            // Show the modal
            modal.style.display = "block";
        });

        // Event listener for close modal button
        document.getElementsByClassName("close")[0].addEventListener("click", function() {
            modal.style.display = "none";
        });

        // Event listener to close modal when clicking outside of it
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };

        // Event listener for register button
        document.getElementById("registerBtn").addEventListener("click", function() {
            const studentName = document.getElementById("id_studentName").value;
            const age = document.getElementById("id_age").value;
            const identificationNumber = document.getElementById("id_identification_number").value;
            const birthdate = document.getElementById("id_birthdate").value;
            const gender = document.getElementById("id_gender").value;
            const race = document.getElementById("id_race").value;
            const teacherName = document.getElementById("id_assigned_teacher").value;
            const parentName = document.getElementById("id_assigned_parent").value;
            const book = document.getElementById("id_book").value;
            const instrument = document.getElementById("id_instrument").value;
            const selectedTimes = selectedSlots.join(", ");
            const selectedDate = document.querySelector('.flatpickr-input').value;

            const data = {
                studentName,
                age,
                identificationNumber,
                birthdate,
                gender,
                race,
                teacherName,
                parentName,
                book,
                instrument,
                selectedTimes,
                selectedDate
            };

            // Perform POST request to register student
            fetch("/register-student/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Student registered successfully:", data);
                // Optionally, close modal or redirect after successful registration
                modal.style.display = "none"; // Close modal after successful registration
            })
            .catch(error => {
                console.error("Error registering student:", error);
                // Handle error: show user-friendly message or log further details
            });
        });

        // Function to retrieve CSRF token from cookies
        function getCSRFToken() {
            const name = 'csrftoken';
            const cookieValue = document.cookie.split('; ')
                .find(cookie => cookie.startsWith(name + '='))
                .split('=')[1];
            return cookieValue;
        }

        // Function to initialize date picker and related functionality
        flatpickr("#flatpickr-calendar", {
            enableTime: false,
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "F j, Y",
            inline: true,
            onChange: function(selectedDates, dateStr, instance) {
                const selectedDate = dateStr; // Store selected date
                console.log('Selected date:', selectedDate); // Debugging
                fetchTeacherClassesByDate(selectedDate); // Fetch classes for selected date
            }
        });

        // Event listener for instrument change
        document.getElementById("id_instrument").addEventListener("change", updateBooks);

        // Event listener for teacher change
        document.getElementById("id_assigned_teacher").addEventListener("change", function() {
            const teacherId = this.value;
            console.log('Selected teacher ID:', teacherId); // Debugging
            fetchTeacherClasses(teacherId); // Fetch classes for selected teacher
        });

        // Function to update book options based on selected instrument
        function updateBooks() {
            const instrumentId = document.getElementById("id_instrument").value;
            fetch(`/get-books/${instrumentId}/`)
                .then(response => response.json())
                .then(data => {
                    const bookField = document.getElementById("id_book");
                    bookField.innerHTML = "";
                    data.books.forEach(book => {
                        const option = document.createElement("option");
                        option.value = book.id;
                        option.textContent = book.book;
                        bookField.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching books:', error);
                });
        }

        // Function to fetch teacher classes by teacher ID
        function fetchTeacherClasses(teacherId) {
            fetch(`/get-teacher-classes/${teacherId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log('Classes fetched:', data.classes); // Log fetched classes array
                    updateCalendar(data.classes); // Update calendar with fetched classes
                    updateStudentList(data.classes); // Update student list with fetched classes
                })
                .catch(error => {
                    console.error('Error fetching teacher classes:', error);
                });
        }

        // Function to fetch teacher classes by date
        function fetchTeacherClassesByDate(dateStr) {
            const teacherId = document.getElementById("id_assigned_teacher").value;
            fetch(`/get-teacher-classes/${teacherId}/?date=${dateStr}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Classes fetched by date:', data.classes); // Log fetched classes array
                    updateCalendar(data.classes); // Update calendar with fetched classes
                    updateStudentList(data.classes); // Update student list with fetched classes
                })
                .catch(error => {
                    console.error('Error fetching teacher classes:', error);
                });
        }

        // Function to update calendar with fetched classes
        function updateCalendar(classes) {
            const calendar = document.getElementById("flatpickr-calendar");
            calendar.innerHTML = ""; // Clear previous content

            classes.forEach(classData => {
                const entry = document.createElement("div");
                entry.innerHTML = `
                    <p>Date: ${classData.date}</p>
                    <p>Time: ${classData.start_time} - ${classData.end_time}</p>
                    <p>Title: ${classData.title}</p>
                    <p>Description: ${classData.description}</p>
                    <p>Student: ${classData.student_name}</p>
                `;
                calendar.appendChild(entry);
            });
        }

        // Function to update student list based on fetched classes
        function updateStudentList(classes) {
            const studentList = document.getElementById("student-list");
            studentList.innerHTML = "<p>Class Slots:</p>";

            // Create a wrapper div for the table-like structure
            const tableWrapper = document.createElement("div");
            tableWrapper.classList.add("table-wrapper");

            // Generate time slots every 30 minutes from 9 am to 9 pm
            for (let hour = 9; hour <= 21; hour++) {
                // Create a row div for each hour
                const rowDiv = document.createElement("div");
                rowDiv.classList.add("table-row");

                for (let minute = 0; minute < 60; minute += 30) {
                    const timeSlotDiv = document.createElement("div"); // Create a div for each time slot
                    timeSlotDiv.classList.add("time-slot"); // Add class to identify time slots
                    const formattedHour = hour < 10 ? `0${hour}` : hour;
                    const formattedMinute = minute === 0 ? "00" : minute;
                    timeSlotDiv.textContent = `${formattedHour}:${formattedMinute}`; // Format time

                    // Search for classes at this time slot
                    const classAtTimeSlot = classes.find(classData => {
                        // Split the time strings to extract only the hour and minute components
                        const startTimeParts = classData.start_time.split(":");
                        const startHour = parseInt(startTimeParts[0]);
                        const startMinute = parseInt(startTimeParts[1]);

                        const endTimeParts = classData.end_time.split(":");
                        const endHour = parseInt(endTimeParts[0]);
                        const endMinute = parseInt(endTimeParts[1]);

                        // Compare class start time and end time with current time slot
                        return (startHour < hour || (startHour === hour && startMinute <= minute)) &&
                            (endHour > hour || (endHour === hour && endMinute > minute));
                    });

                    if (classAtTimeSlot) {
                        // If there's a class, add it to the div
                        const studentDiv = document.createElement("div");
                        studentDiv.innerHTML = `${classAtTimeSlot.student_name} `;
                        studentDiv.style.color = "black"; // Set text color to black
                        timeSlotDiv.appendChild(studentDiv);
                    }

                    // Add event listener to the time slot div
                    timeSlotDiv.addEventListener('click', () => {
                        // Toggle the selection state of the slot
                        toggleSlotSelection(timeSlotDiv);
                    });

                    // Append the time slot div to the row div
                    rowDiv.appendChild(timeSlotDiv);
                }

                // Append the row div to the table wrapper
                tableWrapper.appendChild(rowDiv);
            }

            // Append the table wrapper to the student list container
            studentList.appendChild(tableWrapper);
        }

        // Event listener for teacher change
        document.getElementById("id_assigned_teacher").addEventListener("change", function() {
            const teacherId = this.value;
            const selectedDate = document.querySelector('.flatpickr-input').value; // Get the selected date
            console.log('Selected teacher ID:', teacherId); // Debugging
            fetchTeacherClasses(teacherId, selectedDate); // Fetch classes for selected teacher and date
        });

        // Function to fetch teacher classes by teacher ID and date
        function fetchTeacherClasses(teacherId, selectedDate) {
            let url = `/get-teacher-classes/${teacherId}/`;
            if (selectedDate) {
                url += `?date=${selectedDate}`;
            }
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log('Classes fetched:', data.classes); // Log the fetched classes array
                    updateCalendar(data.classes); // Update calendar with fetched classes
                    updateStudentList(data.classes); // Update student list with fetched classes
                })
                .catch(error => {
                    console.error('Error fetching teacher classes:', error);
                });
        }

        // Function to fetch books based on selected instrument
        function updateBooks() {
            const instrumentId = document.getElementById("id_instrument").value;
            fetch(`/get-books/${instrumentId}/`)
                .then(response => response.json())
                .then(data => {
                    const bookField = document.getElementById("id_book");
                    bookField.innerHTML = "";
                    data.books.forEach(book => {
                        const option = document.createElement("option");
                        option.value = book.id;
                        option.textContent = book.book;
                        bookField.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching books:', error);
                });
        }

        // Function to handle form submission
        document.getElementById("registerBtn").addEventListener("click", function(event) {
            event.preventDefault(); // Prevent default form submission

            // Collect form data
            const studentName = document.getElementById("id_studentName").value;
            const age = document.getElementById("id_age").value;
            const identificationNumber = document.getElementById("id_identification_number").value;
            const birthdate = document.getElementById("id_birthdate").value;
            const gender = document.getElementById("id_gender").value;
            const race = document.getElementById("id_race").value;
            const teacherName = document.getElementById("id_assigned_teacher").value;
            const parentName = document.getElementById("id_assigned_parent").value;
            const book = document.getElementById("id_book").value;
            const instrument = document.getElementById("id_instrument").value;
            const selectedTimes = selectedSlots.join(", ");
            const selectedDate = document.querySelector('.flatpickr-input').value;

            const data = {
                studentName,
                age,
                identificationNumber,
                birthdate,
                gender,
                race,
                teacherName,
                parentName,
                book,
                instrument,
                selectedTimes,
                selectedDate
            };

            // Perform POST request to register student
            fetch("/register-student/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Student registered successfully:", data);
                // Optionally, close modal or redirect after successful registration
                modal.style.display = "none"; // Close modal after successful registration
            })
            .catch(error => {
                console.error("Error registering student:", error);
                // Handle error: show user-friendly message or log further details
            });
        });
    });

    // Function to retrieve CSRF token from cookies
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookieValue = document.cookie.split('; ')
            .find(cookie => cookie.startsWith(name + '='))
            .split('=')[1];
        return cookieValue;
    }


