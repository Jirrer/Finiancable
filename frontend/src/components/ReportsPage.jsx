import { useState, useEffect } from 'react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js'
import { Line, Pie } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler)

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

function monthsAgo(n) {
	const d = new Date()
	d.setMonth(d.getMonth() - n)
	return d.toISOString().slice(0, 7)
}


const timeFrameOptions = [
  { label: "Last 3 Months", value: 3 },
  { label: "Last 6 Months", value: 6 },
  { label: "Last 12 Months", value: 12 },
];

function ReportsPage({ apiBaseUrl }) {
    const defaultMonth = new Date().toISOString().slice(0,7) // YYYY-MM
    const [selectedStartMonth, setSelectedStartMonth] = useState(defaultMonth)
    const [selectedEndMonth, setSelectedEndMonth] = useState(defaultMonth)
    const [purchseChartData, setPurchaseChartData] = useState(null)
	const [incomeChartData, setIncomeChartData] = useState(null)
    const [historyChartData, setHistoryChartData] = useState(null)
	const [selected, setSelected] = useState(12);
	const [selected_range, setSelectedRange] = useState([defaultMonth, defaultMonth])

	const handleSelect = (months) => {
		setSelected(months)
		setSelectedStartMonth(monthsAgo(months - 1)) // -1 so "3 months" includes the current month
		setSelectedEndMonth(defaultMonth)
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
	}, [selectedStartMonth, selectedEndMonth])

    return (
    <div>
		<button className='selected_range'>
			{selected_range[0]} - {selected_range[1]}
			<img src="public/burger-menu.svg" alt="" className='burger_menu' />
		</button>




{/* 
			<div className='date-range'>
				<span>From </span>
				<input type="month" value={selectedStartMonth} onChange={(e) => setSelectedStartMonth(e.target.value)} />
			</div>
			<div className='date-range'>
				<span>To </span>
				<input type="month" value={selectedEndMonth} onChange={(e) => setSelectedEndMonth(e.target.value)} />
			</div>
			<div className="timeframe-selector">
			{timeFrameOptions.map((opt) => (
				<button
				key={opt.value}
				onClick={() => handleSelect(opt.value)}
				className={selected === opt.value ? "active" : ""}
				>
				{opt.label}
				</button>
			))}
			</div> */}
		

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
	</div>
    )
}

export default ReportsPage