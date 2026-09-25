# Backup Rewrite 19th Sep 2026
The current backup method was messy and harder to read due to the requirements of later workflow step paraneters.
The new method moved all of the data required for the workflow into the class itself.
The implementation met all the goals and had produced cleaner, more readable code.

## The Goal
The goal for this rewrite was to push the generated zip files into the object storage container.
This would result in me having a package API that I could call upon which provides proven consistent results compared to a potential custom implementation of my own.
This would also open up the posibility for me to handle any file type of my choosing.
For example, I plan to integrate photo uploading and management for a personnels' day.

## The current issue
With the current backup workflow I was able to easily implement the uploading of generated backup zip files.
However, it would of became increasingly more complex to also have to change the logic for the uploading of a backup file from the client to the application and verifying recorded backup zip files.
The workflow that I had first settled on was as follows: -

1. Create and store a new backup record (store it so that I had a record of backups that passed and failed)
2. Capture the entirety of the database into one file
3. Verify that the generated backup was possible to restore the application data (done in temporary database)
4. Generate backup metadata
5. Compact and zip all generated files as one file
6. Record backup as successful

Currently each step has it's own function that requires data generated from the prior steps in the workflow.
This results in each function gathering and outputing multiple data points in a less orderly fashion.
Also the functions were grouped with the regular BackupService class meaning it now had two purposes it had to fulfill.

## Solution
The current method treated the BackupService class as a library for functions.
The workflow required multiple data points and parameters in order to create a backup of the application.
The data required was also unique only to the workflow minus a few parameters that were saved after completion. 
Therefore, I decided to move towards a class structure where all of the data required would be stored within the class itself.

The pros of this method were clear: -

1. BackupWorkflow and BackupService logic were separate
2. BackupWorkflow function parameters were greatly simplified / present only when required
3. I do not have to worry about correctly transfering the data required for each step
4. The method better handles atomic data

With this the flow of the backups became easier to understand and follow without all the noise from before.

However this method does have some downsides: -

1. It becomes harder to understand the data requirement for each step at a glance
2. It may become harder to manage the parameters that hold the workflow steps data result
3. This method could abstract the underlying majority of the workflow logic

Some of these negatives can be solved with guard clauses and strict parameter management early in its development.
Even though, it still requires someone to view and understand each step of the workflow compared to the prior method.

## Summary
A class has two main purposes in my eyes.
Either a class is a library of functions, similar in scope or a source of truth for malleable data.
For the latter, I have learned one of the effective ways to use a class as a container for atomic data.

With this implementation, it could have been improved upon by allowing compatability with the previous version of backups.
The reason why I did not take this into consideration is:

1. I had no plans to support the old version of backups anymore
2. It would of been extra work for little benefit

The backups from the old version still exist and can be used but if I plan on doing so, it will require a more manual approach.
