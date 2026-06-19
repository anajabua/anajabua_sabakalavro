USE AutomationDB;
GO

-- თუ შემთხვევით უკვე არსებობს, წაშალოს და სუფთად შექმნას
DROP TABLE IF EXISTS Workflows;

CREATE TABLE Workflows (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,                  -- რომელმა იუზერმა შექმნა
    workflow_name NVARCHAR(100) NOT NULL,  -- ავტომატიზაციის სახელი
    steps_json NVARCHAR(MAX) NOT NULL,     -- ბლოკების სტრუქტურა (JSON ტექსტი)
    status NVARCHAR(20) DEFAULT 'active',  
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);
GO

-- შემოწმება, რომ ცხრილი წარმატებით შეიქმნა
SELECT * FROM Workflows;