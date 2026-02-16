document.addEventListener('DOMContentLoaded', () => {
    console.log("Personalize page loaded!");

    const articleData = document.getElementById('articleData');
    const articleId = articleData ? articleData.getAttribute('data-article-id') : null;

    if (!articleId) {
        console.error("Article ID not found!");
        return;
    }

    document.getElementById('generateSummary').addEventListener('click', async () => {
        console.log("Generate Summary button clicked!");
        const summaryType = document.getElementById("summary_type").value;
        const summarySize = document.getElementById("summary_size").value;

        try {
            const response = await fetch('/generate_summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    article_id: articleId,
                    summary_type: summaryType,
                    summary_size: summarySize,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error generating summary:", errorText);
                alert(`Error: ${errorText}`);
                return;
            }

            const result = await response.json();
            if (result.summary) {
                document.getElementById("summaryOutput").innerHTML = `
                    <h2>Generated Summary</h2>
                    <p>${result.summary}</p>
                `;
            } else {
                alert(result.error || "Failed to generate summary");
            }
        } catch (error) {
            console.error("Error generating summary:", error);
            alert("An unexpected error occurred.");
        }
    });
});
