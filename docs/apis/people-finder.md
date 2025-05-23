# People Finder

> This API is available at `/api/peoplefinder/`

The ID service exposes an API that provides read and edit functionality designed for the PeopleFinder / Intranet integration.

### API Endpoints

#### Get Profile:
`/people/<slug>` : returns a minimal peoplefinder profile record
#### Update Profile:
`/people/<slug>` : updates an existing people finder profile and returns a full people finder profile as response
#### Create Profile:
`/people` : creates a new people finder profile and returns a full people finder profile as response
#### Get Teams:
`/teams` : returns all teams in the team hierarchy
#### Get Team:
`/teams/<slug>` : returns a team with its parents, including child-parent relationship depth
#### Create a Team:
`/teams` : creates a new people finder team from the request and returns a minimal team record
#### Update a Team:
`/teams/<slug>` : updates an existing people finder team using the request data and returns a team response 


#### Reference data can be accessed via `/api/peoplefinder/reference/<endpoint>`. Here is the list of reference endpoints:

- `countries` : list of all countries from the database
- `uk_staff_locations` : list of all uk staff locations from the database
- `remote_working` : list of remote working options
- `workdays` : list of workday options
- `learning_interests` : list of learning interests
- `professions` : list of professions
- `grades` : list of grades
- `key_skills` : list of key skills
- `additional_roles` list of additional roles

