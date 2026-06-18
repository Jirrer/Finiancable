import { useState, useRef, useCallback, useEffect, useMemo } from 'react'

function Account({ username, apiBaseUrl, setIsLoggedIn, setUsername, setPassword }) {
    const [userData, setUserData] = useState(null)

    useEffect(() => {
	    fetchUserData();	
	},);

    async function logOut() {
        await fetch(`${apiBaseUrl}/logout`, { method: 'POST', credentials: 'include' });
        setIsLoggedIn(false);
        setUsername('');
        setPassword('');
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

    return (
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
    )
}
                        

export default Account