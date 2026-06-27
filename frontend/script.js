async function uploadResume() {

    const file = document.getElementById("resumeFile").files[0];

    if (!file) {
        alert("Please select a resume!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

       const response = await fetch("/analyze", {
    method: "POST",
    body: formData
});

        const data = await response.json();

        document.getElementById("name").innerHTML = data.name;
        document.getElementById("email").innerHTML = data.email;
        document.getElementById("phone").innerHTML = data.phone;

        document.getElementById("result").style.display = "block";

        document.getElementById("score").innerText =
            data.score + "%";
            document.getElementById("strength").innerText = data.strength;
        document.getElementById("progress-bar").style.width=data.score+"%";
        

        document.getElementById("skills").innerHTML =
            data.skills.map(skill => `<li>${skill}</li>`
            ).join("");

        document.getElementById("missingSkills").innerHTML = data.missing_skills.map(skill =>
                `<li>${skill}</li>`
            ).join("");

        document.getElementById("jobs").innerHTML =
            data.jobs.map(job =>
                `<li>${job}</li>`
            ).join("");

        document.getElementById("feedback").innerHTML =
            data.feedback.map(item =>
                `<li>${item}</li>`
            ).join("");

    } catch (error) {

        console.error(error);
        alert("Backend Connection Failed");
    }
}