import { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import LogData from './components/LogData'
import './App.css'
import { Line, Pie } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler)

function App() {
	const [username, setusername] = useState('')
	const [password, setPassword] = useState('')
	const [showRegister, setShowRegister] = useState(false)
	const [email, setEmail] = useState('')
	const [loginError, setLoginError] = useState('')
	const [isLoggedIn, setIsLoggedIn] = useState(false)
	const [activeScreen, setActiveScreen] = useState('Reports')
	const [purchseChartData, setPurchaseChartData] = useState(null)
	const [incomeChartData, setIncomeChartData] = useState(null)
    const [historyChartData, setHistoryChartData] = useState(null)
	const defaultMonth = new Date().toISOString().slice(0,7) // YYYY-MM
	const [selectedStartMonth, setSelectedStartMonth] = useState(defaultMonth)
	const [selectedEndMonth, setSelectedEndMonth] = useState(defaultMonth)
	const [showLogin, setShowLogin] = useState(true)
	const [userData, setUserData] = useState(null)

	const apiBaseUrl = import.meta.env.DEV
		? import.meta.env.VITE_API_DEV_URL
		: import.meta.env.VITE_API_PROD_URL
	
	function aggregateCategoryTotals(monthlyReport = {}) {
		const months = Object.values(monthlyReport)
		const purchaseTotals = {}
		const incomeTotals = {}

		for (const monthData of months) {
			if (!monthData || typeof monthData !== 'object') continue

			if (monthData.purchase && typeof monthData.purchase === 'object') {
				for (const [category, amount] of Object.entries(monthData.purchase)) {
					purchaseTotals[category] = (purchaseTotals[category] ?? 0) + Number(amount ?? 0)
				}
			}

			if (monthData.income && typeof monthData.income === 'object') {
				for (const [category, amount] of Object.entries(monthData.income)) {
					incomeTotals[category] = (incomeTotals[category] ?? 0) + Number(amount ?? 0)
				}
			}
		}

		return { purchaseTotals, incomeTotals }
	}

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

	function buildPieData(categoryTotals, colors) {
		if (!categoryTotals || typeof categoryTotals !== 'object') return null
		const labels = Object.keys(categoryTotals)
		if (!labels.length) return null

		const sorted = labels
			.map((k) => ({ label: k, value: Math.abs(Number(categoryTotals[k] ?? 0)) }))
			.sort((a, b) => b.value - a.value)

		const sortedLabels = sorted.map((d) => d.label)
		const sortedValues = sorted.map((d) => d.value)
		const labeledLabels = sortedLabels.map((k, i) => `${k}: $${sortedValues[i].toLocaleString()}`) // ← add this back

		return {
			labels: labeledLabels, // ← use labeledLabels instead of sortedLabels
			datasets: [{ data: sortedValues, backgroundColor: colors.slice(0, sortedLabels.length), borderColor: '#fff', borderWidth: 1 }],
		}
	}

	function buildHistoryData(monthlyReport = {}) {
		if (!monthlyReport || typeof monthlyReport !== 'object') return null

		const hasCategoryData = (value) => value && typeof value === 'object' && Object.keys(value).length > 0
		const parseMonthLabel = (label) => {
			const [firstPart, secondPart] = String(label).split(/[/-]/)
			if (!firstPart || !secondPart) return { year: 0, month: 0 }

			if (firstPart.length === 4) {
				return { year: Number(firstPart), month: Number(secondPart) }
			}

			return { year: Number(secondPart), month: Number(firstPart) }
		}

		const labels = Object.keys(monthlyReport)
			.filter((month) => {
			const monthData = monthlyReport?.[month]
			if (!monthData || typeof monthData !== 'object') return false

			const hasTransactions =
				hasCategoryData(monthData.purchase) ||
				hasCategoryData(monthData.income) ||
				hasCategoryData(monthData.transfer)

			const hasNonZeroTotals =
				Number(monthData.profit ?? 0) !== 0 ||
				Number(monthData.gains ?? 0) !== 0 ||
				Number(monthData.losses ?? 0) !== 0

			return hasTransactions || hasNonZeroTotals
			})
			.sort((left, right) => {
				const leftDate = parseMonthLabel(left)
				const rightDate = parseMonthLabel(right)

				if (leftDate.year !== rightDate.year) {
					return leftDate.year - rightDate.year
				}

				return leftDate.month - rightDate.month
			})

		if (!labels.length) return null

		const values = labels.map((month) => Number(monthlyReport?.[month]?.profit ?? 0))
		const points = []
		const labelMap = {}

		labels.forEach((month, index) => {
			const currentValue = values[index]
			const x = index

			points.push({ x, y: currentValue })
			labelMap[x] = month

			if (index === labels.length - 1) return

			const nextValue = values[index + 1]
			const crossesZero = (currentValue < 0 && nextValue > 0) || (currentValue > 0 && nextValue < 0)

			if (!crossesZero) return

			const delta = currentValue - nextValue
			if (delta === 0) return

			const zeroCrossingX = x + currentValue / delta
			points.push({ x: zeroCrossingX, y: 0, synthetic: true })
		})

		return {
			labels,
			datasets: [
				{
					label: 'Profit',
					data: points,
					borderColor: '#0ea5e9',
					segment: {
						borderColor: (context) => {
							const startValue = context.p0.parsed.y
							const endValue = context.p1.parsed.y

							return startValue < 0 || endValue < 0 ? '#ef4444' : '#22c55e'
						},
						backgroundColor: (context) => {
							const startValue = context.p0.parsed.y
							const endValue = context.p1.parsed.y

							return startValue < 0 || endValue < 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)'
						},
					},
					tension: 0.25,
					pointRadius: (context) => (context.raw?.synthetic ? 0 : 4),
					pointHoverRadius: (context) => (context.raw?.synthetic ? 0 : 6),
					pointHitRadius: (context) => (context.raw?.synthetic ? 0 : 8),
					pointBackgroundColor: (context) => (context.raw?.synthetic ? 'transparent' : context.parsed.y < 0 ? '#ef4444' : '#22c55e'),
					pointBorderColor: (context) => (context.raw?.synthetic ? 'transparent' : context.parsed.y < 0 ? '#ef4444' : '#22c55e'),
					fill: true,
				},
			],
			labelMap,
		}
	}

	async function getMonth(monthStart = selectedStartMonth, monthEnd = selectedEndMonth) {
		const url = `${apiBaseUrl}/get-report`
		const start = monthStart <= monthEnd ? monthStart : monthEnd
		const end = monthStart <= monthEnd ? monthEnd : monthStart

		try {
			const response = await fetch(url, {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify({ date_start: start, date_end: end, return_type: 'json' })
				})

			if (response.ok) {
				const json = await response.json()
				
				const report = json?.report ?? {}
				const { purchaseTotals, incomeTotals } = aggregateCategoryTotals(report)
				const purchaseData = buildPieData(purchaseTotals, ['#0ea5e9', '#60a5fa', '#34d399', '#f97316', '#f43f5e'])
				const incomeData = buildPieData(incomeTotals, ['#34d399', '#60a5fa', '#0ea5e9', '#f97316', '#f43f5e'])
				const historyData = buildHistoryData(report)

				return { purchaseData, incomeData, historyData, report }
			} else {
				console.warn('Backend returned non-ok', response.status)
			}
		} catch (err) {
			console.warn('Backend fetch failed', err)
		}

		return { purchaseData: null, incomeData: null, historyData: null, report: null }
	}

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
		if (!isLoggedIn || activeScreen !== 'Reports') {
			return
		}

		if (activeScreen === 'Reports') {
			let mounted = true

			getMonth(selectedStartMonth, selectedEndMonth).then((res) => {
				if (!mounted) return
				setPurchaseChartData(res.purchaseData)
				setIncomeChartData(res.incomeData)
				setHistoryChartData(res.historyData)
			})

			return () => {
				mounted = false
			}
		}
	}, [isLoggedIn, selectedStartMonth, selectedEndMonth, activeScreen])

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
							<div className='date-range-container'>
								<div className='date-range'>
									<span>From </span>
									<input type="month" value={selectedStartMonth} onChange={(e) => setSelectedStartMonth(e.target.value)} />
								</div>
								<div className='date-range'>
									<span>To </span>
									<input type="month" value={selectedEndMonth} onChange={(e) => setSelectedEndMonth(e.target.value)} />
								</div>
							</div>

							<div className='reports'>
								<div className='pie-reports-container'>
									<div className='pie-report' id='purchase-chart'>
										<p className="chart-label">Purchases</p>
										<div className="pie-chart">
											{purchseChartData ? (
												<Pie
													data={purchseChartData}
													options={{
														responsive: true,
														maintainAspectRatio: false,
														plugins: { legend: 
															{ position: 'right',
																labels: {
																	color: '#FFF',
																	font: {
																		size: 14
																	}
																}
															 }
														},
													}}
												/>
											) : (
												<div className="empty-state">No purchase data yet.</div>
											)}
										</div>
									</div>

									<div className='pie-report' id='purchase-chart'>
										<p className="chart-label">Income</p>
										<div className="pie-chart">
											{incomeChartData ? (
												<Pie
													data={incomeChartData}
													options={{
														responsive: true,
														maintainAspectRatio: false,
														plugins: { legend: 
															{ position: 'right',
																labels: {
																	color: '#FFF',
																	font: {
																		size: 14
																	}
																}
															 }
														},
													}}
												/>
											) : (
												<div className="empty-state">No income data yet.</div>
											)}
										</div>
									</div>
								</div>

								<div className="line-report">
									<p className="chart-label">Profit History</p>
									<div className="line-chart">
										{historyChartData ? (
											<Line
												data={historyChartData}
												options={{
													responsive: true,
													maintainAspectRatio: false,
													scales: {
														x: {
															type: 'linear',
															ticks: {
																stepSize: 1,
																callback: (value) => historyChartData?.labelMap?.[value] ?? '',
															},
														},
													},
													plugins: { legend: { display: false }, 
													labels: {
														color: '#FFF',
														font: {
															size: 14
														}
													} },
												}}
											/>
										) : (
											<div className="empty-state">No profit history data yet.</div>
										)}
									</div>
								</div>
							</div>
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