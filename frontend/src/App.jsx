import { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import LogData from './components/LogData'
import Account from './components/Account'
import Report from './components/Reports'
import './App.css'

function App() {
	const [username, setusername] = useState('')
	const [password, setPassword] = useState('')
	const [showRegister, setShowRegister] = useState(false)
	const [email, setEmail] = useState('')
	const [loginError, setLoginError] = useState('')
	const [isLoggedIn, setIsLoggedIn] = useState(false)
	const [activeScreen, setActiveScreen] = useState('Reports')
	const [showLogin, setShowLogin] = useState(true)
	const [userData, setUserData] = useState(null)

	const apiBaseUrl = import.meta.env.DEV
		? import.meta.env.VITE_API_DEV_URL
		: import.meta.env.VITE_API_PROD_URL
	

function EditableTransactionsTable({ transactions = [], onChange }) {
	// columns = union of keys across all transaction objects
	const columns = useMemo(() => {
		const cols = new Set()
		for (const t of transactions) {
			if (t && typeof t === 'object' && !Array.isArray(t)) {
				Object.keys(t).forEach((k) => cols.add(k))
			}
		}
		return Array.from(cols)
	}, [transactions])

	const handleCellChange = (rowIndex, key, value) => {
		const copy = transactions.map((r) => (r && typeof r === 'object' ? { ...r } : r))
		const row = copy[rowIndex]
		if (row && typeof row === 'object') {
			// try to preserve types: if original was number, attempt parse
			const orig = row[key]
			if (typeof orig === 'number') {
				const n = Number(value)
				row[key] = Number.isNaN(n) ? value : n
			} else {
				row[key] = value
			}
		} else {
			copy[rowIndex] = value
		}
		onChange(copy)
	}

	if (!transactions || !transactions.length) return <div className="empty-state">No transactions to edit</div>

	return (
		<div style={{ overflowX: 'auto' }}>
			<table className="transactions-table">
				<thead>
					<tr>
						<th>#</th>
						{columns.map((c) => <th key={c}>{c}</th>)}
					</tr>
				</thead>
				<tbody>
					{transactions.map((t, ri) => (
						<tr key={ri}>
							<td style={{ whiteSpace: 'nowrap' }}>{ri + 1}</td>
							{columns.map((c) => (
								<td key={c}>
									{t && typeof t === 'object' && c in t ? (
										<input
											value={t[c] ?? ''}
											onChange={(e) => handleCellChange(ri, c, e.target.value)}
											style={{ width: 160 }}
										/>
									) : (
										<input value={''} onChange={(e) => handleCellChange(ri, c, e.target.value)} style={{ width: 160 }} />
									)}
								</td>
							))}
						</tr>
					))}
				</tbody>
			</table>
		</div>
	)
}

	const fetchUserData = async () => {
		try {
			const response = await fetch(`${apiBaseUrl}/get-user-data`, {
				method: 'GET',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
			});

			if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

			const data = await response.json();
			setUserData(data.report);
		} catch (error) {
			console.error(error);
		}
	};


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


	useEffect(() => {
	if (activeScreen === 'Account') {
		fetchUserData();
		
	}
	}, [activeScreen]);

	if (isLoggedIn) {
		const screenTitle = activeScreen === 'Reports' ? 'Reports' : 'Log-Data'

		return (
			<main className="app-shell">
				<header className="top-bar">
					<div className='user-information'>
                        <button
							onClick={() => setActiveScreen('Account')}
						> <img src="profile-user-account.png" alt="Search"/>
						</button>
					</div>
				</header>
			
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
				</nav>

				<section className="screen-card">
					{activeScreen === 'Reports' && (
						<>							
							<Report apiBaseUrl={apiBaseUrl}></Report>
						</>	
                        
					)}

					{activeScreen === 'Log-Data' && (
						<div>
						<LogData apiBaseUrl={apiBaseUrl} />
						</div>
					)}

					{activeScreen === 'Account' && (
						<div className='account-page'>
							<div className='user-info'>
								{username}
								<button onClick={logOut}>Sign Out</button>
							</div>


							 <div className='accountData'>Net Worth: ${Math.round(userData?.NetWorth?.Networth ?? 0).toLocaleString()}</div>
							<div className='accountData'>Salary: ${userData?.Salary?.toLocaleString() ?? '—'}</div>
							<div className='accountData'>
								Emergency Fund: ${userData?.["Emergency Fund"]?.[0]?.toLocaleString() ?? '—'} – ${userData?.["Emergency Fund"]?.[1]?.toLocaleString() ?? '—'}
							</div>

						</div>
					)}
                    </section>
			</main>
		)
	}

	async function handleSubmit(event) {
		event.preventDefault()

		if (!username.trim() || !password.trim()) {
			setLoginError('Enter your username and password to continue.')
			return
		}

		const loginResponse = await login()

		if (loginResponse && loginResponse.ok) {
			setLoginError('')
			setIsLoggedIn(true)
			setActiveScreen('Reports')
		} else if (loginResponse) {
			try {
				const loginData = await loginResponse.json()
				setLoginError(loginData.error || loginData.message || 'Login failed')
			} catch (e) {
				setLoginError('Login failed')
			}
		}
	}

	async function login() {
		const url = `${apiBaseUrl}/login`

		try {
			const response = await fetch(url, {
				method: 'POST',
				credentials: 'include', 
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: username.trim(), password }),
			})

			return response
		} catch (err) {
			console.warn('Backend fetch failed', err)
			return null
		}
	}

	async function register() {
		const url = `${apiBaseUrl}/register`

		if (!username.trim() || !password) {
			setLoginError('Enter username and password to register')
			return null
		}

		try {
			const registerResponse = await fetch(url, {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: username.trim(), password, email: email?.trim() || null }),
			})

			if (registerResponse.ok) {
				setShowRegister(false)
				setIsLoggedIn(true)
				return registerResponse
			}

			try {
				const registerData = await registerResponse.json()
				setLoginError(registerData.error || registerData.message || 'Registration failed')
			} catch (e) {
				setLoginError('Registration failed')
			}
			return registerResponse
		} catch (err) {
			console.warn('Backend fetch failed', err)
			setLoginError('Registration failed')
			return null
		}
	}

	async function logOut() {
		await fetch(`${apiBaseUrl}/logout`, { method: 'POST', credentials: 'include' });
		setIsLoggedIn(false);
		setusername('');
		setPassword('');
	}

	return (
		<div className="login_screen">
			<div className='login_directions'>
				<button onClick={() => setShowLogin(true)}>Login</button>
				<p> | </p>
				<button onClick={() => setShowLogin(false)}>Sign-Up</button>
			</div>
			{
				showLogin ? (
					<>
						<form action="" className="login_form">
							<div className='login_input'>
								<input 
									type='username'
									name='username'
									id='username'
									placeholder='Username'
									onChange={(event) => setusername(event.target.value)}
									required>
								</input>

								<input 
									type='password' 
									name='password' 
									id='password' 
									placeholder='Password' 
									onChange={(event) => setPassword(event.target.value)}
									required>

								</input>
							</div>

							<button
								type="button"
								className="primary-button"
								onClick={handleSubmit}
								>
								Login
							</button>
						</form>

						{loginError ? <p className="error-message">{loginError}</p> : null}
	
					</>
				) : (
					<>
						<form action="" className="login_form">
							<div className='login_input'>
								<input
									type='username'
									name='username'
									id='username'
									placeholder='Username'
									onChange={(event) => setusername(event.target.value)}
									required>
								</input>

								<input 
									type='password'
									name='password'
									id='password'
									placeholder='Password'
									onChange={(event) => setPassword(event.target.value)}
									required>
								</input>

								<input
								type='email'
								name='email'
								id='email'
								onChange={(e) => setEmail(e.target.value)}
								placeholder='emal'>
								</input>
							</div>

							<button
								type="button"
								className="primary-button"
								onClick={async () => {
									const resp = await register()
									if (resp && resp.ok) {
										setLoginError('')
										setIsLoggedIn(true)
										setActiveScreen('Reports')
									}
								}}
								>
								Register
							</button>
						</form>

						{loginError ? <p className="error-message">{loginError}</p> : null}
					</>
				)
			}
		</div>
	)

}

export default App