// Resume Upload
document.getElementById("resume-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const userId = document.getElementById("resume-user-id").value;
    const resumeFile = document.getElementById("resume-file").files[0];
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("resume", resumeFile);
    
    fetch("http://127.0.0.1:5000/upload_resume", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("upload-result").innerText = data.status === "success" ?
            `Uploaded! Skills: ${data.skills.join(", ")}, Experience: ${data.experience} years` :
            `Error: ${data.message}`;
    })
    .catch(error => console.error("Error:", error));
});

// Manual Entry (Candidates)
document.getElementById("manual-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const userId = document.getElementById("manual-user-id").value;
    const skills = document.getElementById("skills").value;
    const experience = document.getElementById("experience").value;
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("skills", skills);
    formData.append("experience", experience);

    fetch("http://127.0.0.1:5000/add_manual", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("manual-result").innerText = data.status === "success" ?
            `Saved! Skills: ${data.skills.join(", ")}, Experience: ${data.experience} years` :
            `Error saving data`;
    })
    .catch(error => console.error("Error:", error));
});

// Add Job Posting
document.getElementById("job-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const title = document.getElementById("job-title").value;
    const requiredSkills = document.getElementById("required-skills").value;
    const formData = new FormData();
    formData.append("title", title);
    formData.append("required_skills", requiredSkills);
    
    

    fetch("http://127.0.0.1:5000/add_job", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("job-result").innerText = data.status === "success" ?
            `Job Added! Title: ${data.title}, Required Skills: ${data.required_skills}` :
            `Error adding job`;
    })
    .catch(error => console.error("Error:", error));
});

// Search Candidates
function searchCandidates() {
    const skills = document.getElementById("skills-input").value;
    const messageDiv = document.getElementById("search-result-message");
    const rankedList = document.getElementById("ranked-list");
    messageDiv.innerText = "";
    rankedList.innerHTML = "loading...";

    const query = skills ? `skills=${encodeURIComponent(skills)}` : `job_id=1`;  // Example job_id=1 if no skills
    fetch(`http://127.0.0.1:5000/rank_users?${query}`)
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            rankedList.innerHTML = "";
            messageDiv.innerText = data.message;
        } else {
            rankedList.innerHTML = "";

            data.forEach(user => {
                const tr = document.createElement("tr");
                const userTd = document.createElement("td");
                userTd.innerText = `User ${user.user_id}`;
                const scoreTd = document.createElement("td");
                scoreTd.innerText = `${user.score} points`;
                const skillsTd = document.createElement("td");
                skillsTd.innerText = user.skills.join(", ") || "No skills";
                const summaryTd = document.createElement("td");
                summaryTd.innerText = user.summary;
                tr.appendChild(userTd);
                tr.appendChild(scoreTd);
                tr.appendChild(skillsTd);
                tr.appendChild(summaryTd);
                rankedList.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
        messageDiv.innerText = "Error fetching candidates";
    });
}