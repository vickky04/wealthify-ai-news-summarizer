document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('adminLoginForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = {
            email: formData.get('adminEmail'),
            password: formData.get('adminPassword')
        };
        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                window.location.href = '/admin';
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});
