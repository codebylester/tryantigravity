document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('user-question');
    const generateBtn = document.getElementById('generate-btn');
    const resultSection = document.getElementById('result-section');
    const sqlOutput = document.getElementById('sql-output');
    const copyBtn = document.getElementById('copy-btn');
    const toast = document.getElementById('toast');
    const btnText = generateBtn.querySelector('span');
    const spinner = generateBtn.querySelector('.loading-spinner');
    const uploadInput = document.getElementById('schema-upload');
    const uploadBtn = document.getElementById('upload-btn');
    const schemaStatus = document.getElementById('schema-status');
    const helperBtns = document.querySelectorAll('.db-helper-btn');
    const helperContainer = document.getElementById('helper-query-container');
    const helperText = document.getElementById('helper-query-text');
    const copyHelperBtn = document.getElementById('copy-helper-btn');

    // Schema Extraction Queries
    const queries = {
        postgres: `-- PostgreSQL: Get table definitions
SELECT 
    'CREATE TABLE ' || table_name || ' (' || 
    string_agg(column_definition, ', ') || ');' 
FROM (
    SELECT 
        table_name,
        column_name || ' ' || data_type || 
        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END AS column_definition
    FROM information_schema.columns
    WHERE table_schema = current_schema()
    ORDER BY table_name, ordinal_position
) sub
GROUP BY table_name;`,

        mysql: `-- MySQL: Get table definitions
SELECT 
    CONCAT('CREATE TABLE ', table_name, ' (', 
    GROUP_CONCAT(column_name, ' ', column_type, 
    IF(is_nullable = 'NO', ' NOT NULL', '')), ');')
FROM information_schema.columns
WHERE table_schema = DATABASE()
GROUP BY table_name;`,

        sqlite: `-- SQLite: Get all table schemas
SELECT sql || ';' FROM sqlite_master 
WHERE type='table' AND name NOT LIKE 'sqlite_%';`
    };

    // Load schema on startup
    async function loadSchema() {
        try {
            const response = await fetch('/api/schema');
            if (response.ok) {
                const data = await response.json();
                // We no longer display the schema text in the UI
                console.log("Schema context verified.");
            }
        } catch (error) {
            console.error('Error loading schema:', error);
        }
    }

    loadSchema();

    // Generate SQL function
    async function generateSQL() {
        const question = questionInput.value.trim();
        if (!question) return;

        // UI State: Loading
        generateBtn.disabled = true;
        btnText.textContent = "Connecting to Gemini...";
        spinner.classList.remove('hidden');
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();

            if (response.ok) {
                sqlOutput.textContent = data.sql;
                resultSection.classList.remove('hidden');

                // Smooth scroll to result
                setTimeout(() => {
                    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);
            } else {
                alert("Error: " + (data.error || "Failed to generate SQL"));
            }
        } catch (error) {
            console.error('Error:', error);
            alert("Connection error. Is the server running?");
        } finally {
            // UI State: Reset
            generateBtn.disabled = false;
            btnText.textContent = "Generate SQL";
            spinner.classList.add('hidden');
        }
    }

    // Event Listeners
    generateBtn.addEventListener('click', generateSQL);

    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateSQL();
        }
    });

    copyBtn.addEventListener('click', () => {
        const sql = sqlOutput.textContent;
        navigator.clipboard.writeText(sql);

        // Show toast
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 2500);
    });

    // Handle schema upload
    uploadBtn.addEventListener('click', () => uploadInput.click());

    uploadInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const isCSV = file.name.toLowerCase().endsWith('.csv');
        const isSQL = file.name.toLowerCase().endsWith('.sql');

        if (!isCSV && !isSQL) {
            alert("Please upload a .sql or .csv file.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // UI State: Uploading
        uploadBtn.disabled = true;
        const originalText = uploadBtn.querySelector('span').textContent;
        uploadBtn.querySelector('span').textContent = isCSV ? "Analyzing CSV..." : "Uploading...";
        schemaStatus.textContent = isCSV ? "Inferring..." : "Updating...";
        schemaStatus.style.background = "rgba(245, 158, 11, 0.1)";
        schemaStatus.style.color = "#f59e0b";

        try {
            const response = await fetch('/api/upload-schema', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                schemaStatus.textContent = "Loaded: " + file.name;
                schemaStatus.style.background = "rgba(16, 185, 129, 0.1)";
                schemaStatus.style.color = "#10b981";

                // Show toast for success
                const originalToast = toast.textContent;
                toast.textContent = isCSV ? "CSV Schema Generated!" : "Schema updated!";
                toast.classList.remove('hidden');

                // Reload schema preview context in agent
                await loadSchema();

                setTimeout(() => {
                    toast.classList.add('hidden');
                    setTimeout(() => toast.textContent = originalToast, 500);
                }, 2500);
            } else {
                alert("Upload failed: " + data.error);
                schemaStatus.textContent = "Error";
                schemaStatus.style.background = "rgba(239, 68, 68, 0.1)";
                schemaStatus.style.color = "#ef4444";
            }
        } catch (error) {
            console.error('Error:', error);
            alert("Upload connection error.");
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.querySelector('span').textContent = originalText;
        }
    });

    // Helper Button Logic
    helperBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const db = btn.dataset.db;

            // Toggle active state
            helperBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show query
            helperText.textContent = queries[db];
            helperContainer.classList.remove('hidden');
        });
    });

    copyHelperBtn.addEventListener('click', () => {
        const query = helperText.textContent;
        navigator.clipboard.writeText(query);

        toast.textContent = "Query copied!";
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
            setTimeout(() => toast.textContent = "Copied to clipboard!", 500);
        }, 2000);
    });
});
