async function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch('/', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (data.error) {
        alert(data.error);
    } else {
        // Update DOM with results
    }
}