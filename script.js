
function validate(unames, emails)
{
    var name = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    let email = document.getElementById("email").value;
    var alert = document.getElementById("msg");

    // want to perform these checks
    // the password should include at least one
    //upper case letter, one lower case letter, one digit and one of these symbols [+, !, *, -] and its length
    //should be at least ten.

    for (var i = 0; i < unames.length; i++)
    {
        if (unames[i] == name)
        {
            alert.innerHTML = "Username already exists!";
            return false;
        }
        if(emails[i] == email)
        {
            alert.innerHTML = "Email already exists!"
            return false;
        }

    }

    if (password.length < 10)
    {
        alert.innerHTML = "Password should be at least 10 characters long";
        return false;
    }
    // using regex for password validation using the search method
    else if(password.search(/[a-z]/) == -1)
    {
        alert.innerHTML = "Password should have at least one lower case letter";
        return false;
    }
    else if(password.search(/[A-Z]/) == -1)
    {
        alert.innerHTML = "Password should have at least one upper case letter";
        return false;
    }
    else if(password.search(/[0-9]/) == -1)
    {
        alert.innerHTML = "Password should have at least one digit";
        return false;
    }
    else if(password.search(/[\+\!\*\-]/) == -1)
    {
        alert.innerHTML = "Password should have at least one of these symbols [+, !, *, -]";
        return false;
    }
    else
    {
        alert.innerHTML = "";
        return true;
    }

    return true;
}

// function enableEdit(button) {
//   const row = button.closest('tr');
//   row.querySelectorAll('[contenteditable]').forEach(cell => {
//     cell.setAttribute('contenteditable', 'true');
//     cell.classList.add('bg-yellow-100');  // Optional: add a background color to indicate editable cells
//   });
//   button.nextElementSibling.classList.add('hidden');  // Hide "Delete" button
//   button.classList.add('hidden');  // Hide "Update" button
//   button.nextElementSibling.nextElementSibling.classList.remove('hidden');  // Show "Save" button
//   button.nextElementSibling.nextElementSibling.nextElementSibling.classList.remove('hidden');  // Show "Cancel" button
// }
//
// function saveRow(button) {
//   const row = button.closest('tr');
//   const data = {};
//   row.querySelectorAll('[data-field]').forEach(cell => {
//     data[cell.getAttribute('data-field')] = cell.textContent.trim();
//     cell.removeAttribute('contenteditable');
//     cell.classList.remove('bg-yellow-100');  // Optional: remove the background color
//   });
//
//   // Send the updated data to the server
//   fetch('/profile/update_event', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify(data),
//   })
//   .then(response => response.json())
//   .then(result => {
//     console.log('Success:', result);
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   });
//
//   button.previousElementSibling.classList.remove('hidden');  // Show "Update" button
//   button.previousElementSibling.previousElementSibling.classList.remove('hidden');  // Show "Delete" button
//   button.classList.add('hidden');  // Hide "Save" button
//   button.nextElementSibling.classList.add('hidden');  // Hide "Cancel" button
// }
//
// function cancelEdit(button) {
//   const row = button.closest('tr');
//   row.querySelectorAll('[data-field]').forEach(cell => {
//     cell.textContent = cell.getAttribute('data-original');
//     cell.removeAttribute('contenteditable');
//     cell.classList.remove('bg-yellow-100');  // Optional: remove the background color
//   });
//   button.previousElementSibling.classList.remove('hidden');  // Show "Update" button
//   button.previousElementSibling.previousElementSibling.classList.remove('hidden');  // Show "Delete" button
//   button.classList.add('hidden');  // Hide "Cancel" button
//   button.previousElementSibling.previousElementSibling.previousElementSibling.classList.add('hidden');  // Hide "Save" button
// }
//
// function deleteRow(button) {
//   const row = button.closest('tr');
//   const eventId = row.querySelector('[data-field="event_id"]').textContent.trim();
//
//   fetch(/delete_event/${eventId}, {
//     method: 'DELETE',
//   })
//   .then(response => response.json())
//   .then(result => {
//     console.log('Success:', result);
//     row.remove();
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   });
// }