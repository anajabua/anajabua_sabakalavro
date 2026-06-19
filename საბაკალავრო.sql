USE AutomationDB;
GO

DROP TABLE IF EXISTS Workflows;

CREATE TABLE Workflows (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,                  
    workflow_name NVARCHAR(100) NOT NULL,  
    steps_json NVARCHAR(MAX) NOT NULL,     
    status NVARCHAR(20) DEFAULT 'active',  
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
GO

SELECT * FROM Workflows;
