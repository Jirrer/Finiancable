import { useState, useRef, useCallback, useEffect, useMemo } from 'react'

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

// Helper: format bytes to human readable
function formatBytes(bytes) {
	if (!bytes && bytes !== 0) return ''
	const thresh = 1024
	if (Math.abs(bytes) < thresh) return bytes + ' B'
	const units = ['KB', 'MB', 'GB', 'TB']
	let u = -1
	do {
		bytes /= thresh
		++u
	} while (Math.abs(bytes) >= thresh && u < units.length - 1)
	return bytes.toFixed( (bytes >= 10 || u === 0) ? 0 : 1 ) + ' ' + units[u]
}

// Helper: very small CSV parser (headers + rows)
function parseCSV(text) {
	if (!text) return { headers: [], rows: [] }
	const lines = text.split(/\r?\n/).filter((l) => l.trim() !== '')
	if (!lines.length) return { headers: [], rows: [] }
	const headers = lines[0].split(/,|\t/).map((h) => h.trim())
	const rows = lines.slice(1).map((ln) => ln.split(/,|\t/).map((c) => c.trim()))
	return { headers, rows }
}

function CSVPreview({ file, onRemove }) {
	const [parsed, setParsed] = useState({ headers: [], rows: [] })

	useEffect(() => {
		let cancelled = false
		const reader = new FileReader()
		reader.onload = (e) => {
			if (cancelled) return
			try {
				const text = e.target.result
				setParsed(parseCSV(text))
			} catch (err) {
				setParsed({ headers: [], rows: [] })
			}
		}
		reader.onerror = () => {
			if (!cancelled) setParsed({ headers: [], rows: [] })
		}
		reader.readAsText(file)

		return () => {
			cancelled = true
		}
	}, [file])

	const rowCount = parsed.rows.length
	const showRows = parsed.rows.slice(0, 10)

	return (
		<div className="csv-card">
			<div className="csv-card-header">
				<div>
					<strong>{file.name}</strong> — {formatBytes(file.size)} — {rowCount} rows
				</div>
				<button className="csv-remove" onClick={() => onRemove(file)}>✕</button>
			</div>

			<div className="csv-preview-table">
				{parsed.headers.length ? (
					<table>
						<thead>
							<tr>{parsed.headers.map((h, i) => <th key={i}>{h}</th>)}</tr>
						</thead>
						<tbody>
							{showRows.map((r, ri) => (
								<tr key={ri}>{r.map((c, ci) => <td key={ci}>{c}</td>)}</tr>
							))}
						</tbody>
					</table>
				) : (
					<div className="empty-state">No preview available</div>
				)}

				{rowCount > 10 ? <div className="note">Showing first 10 of {rowCount} rows</div> : null}
			</div>
		</div>
	)
}

function LogDataPage({ apiBaseUrl }) {
	const [files, setFiles] = useState([])
	const [dragging, setDragging] = useState(false)
	const inputRef = useRef(null)
	const [uploading, setUploading] = useState(false)
	const [result, setResult] = useState(null)
	const [uploadError, setUploadError] = useState('')
	const [editableTransactions, setEditableTransactions] = useState(null)
	const [saving, setSaving] = useState(false)
	const [saveError, setSaveError] = useState('')

	const addFiles = useCallback((incomingFiles) => {
		const allowed = ['csv', 'tsv', 'xlsx']
		const arr = Array.from(incomingFiles).filter((f) => {
			const ext = (f.name.split('.').pop() || '').toLowerCase()
			return allowed.includes(ext)
		})

		// dedupe by name+size
		const existingKeys = new Set(files.map((f) => `${f.name}:${f.size}`))
		const toAdd = arr.filter((f) => !existingKeys.has(`${f.name}:${f.size}`))
		if (!toAdd.length) return
		setFiles((s) => s.concat(toAdd))
	}, [files])

	const onDrop = useCallback((e) => {
		e.preventDefault()
		setDragging(false)
		addFiles(e.dataTransfer.files)
	}, [addFiles])

	const onFileInput = useCallback((e) => {
		addFiles(e.target.files)
		e.target.value = null
	}, [addFiles])

	const removeFile = useCallback((file) => {
		setFiles((s) => s.filter((f) => !(f.name === file.name && f.size === file.size)))
	}, [])

	const clearAll = useCallback(() => { setFiles([]); setResult(null); setUploadError('') }, [])

	return (
		<div>
			<input ref={inputRef} style={{ display: 'none' }} type="file" multiple onChange={onFileInput} />

			<div
				className={`drop-zone ${dragging ? 'dragging' : ''}`}
				onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
				onDragLeave={() => setDragging(false)}
				onDrop={onDrop}
				onClick={() => inputRef.current && inputRef.current.click()}
				role="button"
			>
				<p>Drop CSV/TSV/XLSX files here, or click to select</p>
			</div>

			{files.length ? (
				<div className="files-actions">
					<span>{files.length} file(s) selected</span>
					<div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
						<button onClick={clearAll} disabled={uploading}>Clear all</button>
						<button onClick={async () => {
							setUploading(true)
							setUploadError('')
							setResult(null)
							try {
								if (!apiBaseUrl) {
									setUploadError('API base URL not configured (VITE_API_BASE_URL)')
									setUploading(false)
									return
								}
								const fd = new FormData()
								for (const f of files) fd.append('report', f)
								fd.append('returnType', 'JSON')
								// include internal_transfers if needed: fd.append('internal_transfers', '')

								const resp = await fetch(`${apiBaseUrl}/create-report`, {
									method: 'POST',
									credentials: 'include',
									body: fd,
								})

								if (!resp.ok) {
									const txt = await resp.text()
									setUploadError(`Server error: ${resp.status} ${txt}`)
								} else {
									const json = await resp.json()
									setResult(json)
									// set editable transactions (if present) so user can edit inline
									setEditableTransactions(Array.isArray(json.transactions) ? json.transactions.map((t) => ({ ...t })) : null)
									// clear the selected files while keeping the result visible
									setFiles([])
								}
							} catch (err) {
								console.warn('Upload failed', err)
								setUploadError(String(err))
							} finally {
								setUploading(false)
							}
						}} disabled={uploading}>
							{uploading ? 'Uploading…' : 'Create Report'}
						</button>
					</div>
				</div>
			) : null}

			<div className="csv-previews">
				{files.map((f) => (
					<CSVPreview key={`${f.name}:${f.size}`} file={f} onRemove={removeFile} />
				))}
			</div>

			{uploadError ? <div className="error-message">{uploadError}</div> : null}

			{result ? (
				<section className="report-result">
					<h3>Create Report Result</h3>
					<div>Transactions: {Array.isArray(result.transactions) ? result.transactions.length : 'N/A'}</div>

					{Array.isArray(result.transactions) ? (
						<div>
							<div style={{ margin: '8px 0', display: 'flex', gap: 8 }}>
								<button onClick={async () => {
									// Save edited transactions to backend /upload-report
									if (!apiBaseUrl) { setSaveError('API base URL not configured'); return }
									setSaving(true); setSaveError('')
									try {
										// backend expects a dict (object) of transactions, not an array
										const txRaw = editableTransactions ?? result.transactions
										let txPayload
										if (Array.isArray(txRaw)) {
											txPayload = {}
											txRaw.forEach((t, idx) => { txPayload[idx] = t })
										} else {
											txPayload = txRaw
										}

										const resp = await fetch(`${apiBaseUrl}/upload-report`, {
											method: 'POST',
											credentials: 'include',
											headers: { 'Content-Type': 'application/json' },
											body: JSON.stringify({ transactions: txPayload }),
										})
										if (!resp.ok) {
											const txt = await resp.text()
											setSaveError(`Server error: ${resp.status} ${txt}`)
										} else {
											// on success clear the UI (previews, result, edits)
											const j = await resp.json().catch(() => null)
											clearAll()
											setEditableTransactions(null)
											// transient success message
											setSaveError(j && j.Status ? `Saved: ${j.Status}` : 'Saved successfully')
											setTimeout(() => setSaveError(''), 2500)
										}
									} catch (err) {
										console.warn('Save failed', err)
										setSaveError(String(err))
									} finally {
										setSaving(false)
									}
								}} disabled={saving}>{saving ? 'Saving…' : 'Save Edited'}</button>

								<button onClick={() => setEditableTransactions(Array.isArray(result.transactions) ? result.transactions.map((t) => ({ ...t })) : null)}>Reset Edits</button>
							</div>

							<EditableTransactionsTable
								transactions={editableTransactions ?? result.transactions}
								onChange={setEditableTransactions}
							/>
						</div>
					) : (
						<pre style={{ maxHeight: 400, overflow: 'auto',  padding: 12 }}>{JSON.stringify(result, null, 2)}</pre>
					)}

					{saveError ? <div className="info-message">{saveError}</div> : null}
				</section>
			) : null}
		</div>
	)
}

export default LogDataPage