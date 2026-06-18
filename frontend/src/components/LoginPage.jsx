import { useState } from 'react'

function LoginPage({ apiBaseUrl, onLoginSuccess }) {
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [email, setEmail] = useState('')
	const [showLogin, setShowLogin] = useState(true)
	const [loginError, setLoginError] = useState('')

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

			if (!registerResponse.ok) {
				try {
					const registerData = await registerResponse.json()
					setLoginError(registerData.error || registerData.message || 'Registration failed')
				} catch (e) {
					setLoginError('Registration failed')
				}
			}

			return registerResponse
		} catch (err) {
			console.warn('Backend fetch failed', err)
			setLoginError('Registration failed')
			return null
		}
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
			onLoginSuccess(username.trim())
		} else if (loginResponse) {
			try {
				const loginData = await loginResponse.json()
				setLoginError(loginData.error || loginData.message || 'Login failed')
			} catch (e) {
				setLoginError('Login failed')
			}
		}
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
									onChange={(event) => setUsername(event.target.value)}
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
									onChange={(event) => setUsername(event.target.value)}
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
										onLoginSuccess(username.trim())
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

export default LoginPage