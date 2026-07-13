import { useState, useCallback, useEffect } from 'react'
import LoginPage from './components/LoginPage'
import LogDataPage from './components/LogDataPage'
import AccountPage from './components/AccountPage'
import ReportsPage from './components/ReportsPage'
import './App.css'

function App() {
	const [username, setusername] = useState('')
	const [password, setPassword] = useState('')
	const [showRegister, setShowRegister] = useState(false)
	const [email, setEmail] = useState('')
	const [isLoggedIn, setIsLoggedIn] = useState(false)
	const [activeScreen, setActiveScreen] = useState('Reports')
	const [userData, setUserData] = useState(null)

	const apiBaseUrl = import.meta.env.DEV
		? import.meta.env.VITE_API_DEV_URL
		: import.meta.env.VITE_API_PROD_URL

	useEffect(() => {
		fetch(`${apiBaseUrl}/valid-user`, {
			credentials: 'include'
		})
		.then(res => {
			if (res.ok) return res.json()
			throw new Error('Not logged in')
		})
		.then(data => {
			setusername(data.user.username)
			setIsLoggedIn(true)
		})
		.catch(() => {
			// not logged in, do nothing
		})
	}, [])

	if (isLoggedIn) {
		const screenTitle = activeScreen === 'Reports' ? 'Reports' : 'Log-Data'

		return (
			<main className="app-shell">
				<nav className='nav-buttons'>
					<button
						type="button"
						className={`screen-button ${activeScreen === 'Reports' ? 'active' : ''}`}
						onClick={() => setActiveScreen('Reports')}
					>
						Reports
					</button>

					<button
						type="button"
						className={`screen-button ${activeScreen === 'Log-Data' ? 'active' : ''}`}
						onClick={() => setActiveScreen('Log-Data')}
					>
						Log Data
					</button>

					<button className='user-information'
						onClick={() => setActiveScreen('Account')}
					> <img src='public/profile-user-account.svg' alt="pfp"/>
					</button>
				</nav>

				<section className="screen-card">
					{activeScreen === 'Reports' && (
						<>							
							<ReportsPage apiBaseUrl={apiBaseUrl}></ReportsPage>
						</>	
                        
					)}

					{activeScreen === 'Log-Data' && (
						<div>
						<LogDataPage apiBaseUrl={apiBaseUrl} />
						</div>
					)}

					{activeScreen === 'Account' && (
						<div>
							<AccountPage
								username={username} 
								apiBaseUrl={apiBaseUrl}
								setIsLoggedIn={setIsLoggedIn}
								setUsername={setusername}
								setPassword={setPassword}
							/>
						</div>
					)}
                    </section>
			</main>
		)
	}

	return (
		<>
			<LoginPage
				apiBaseUrl={apiBaseUrl}
				onLoginSuccess={(loggedInUsername) => {
					setusername(loggedInUsername)
					setIsLoggedIn(true)
					setActiveScreen('Reports')
				}}
			/>
		</>
	)

}

export default App