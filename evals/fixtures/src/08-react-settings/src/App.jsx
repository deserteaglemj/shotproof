const nav = ['Profile', 'Account', 'Notifications', 'Billing', 'Team', 'Integrations']

const toggles = [
  { label: 'Weekly summary', hint: 'A short email every Monday with last week\'s activity.', on: true },
  { label: 'Mentions', hint: 'Tell me when someone mentions me in a comment.', on: true },
  { label: 'Product updates', hint: 'New features and changes, about once a month.', on: false },
]

function Field({ label, value, hint, wide }) {
  return (
    <label className={wide ? 'col-span-2' : ''}>
      <span className="block text-sm font-medium text-slate-700">{label}</span>
      <span className="mt-1.5 block rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm">{value}</span>
      {hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  )
}

function Toggle({ on }) {
  return (
    <span className={`relative inline-flex h-6 w-11 shrink-0 rounded-full ${on ? 'bg-teal-600' : 'bg-slate-300'}`}>
      <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow ${on ? 'left-5.5' : 'left-0.5'}`} />
    </span>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-8">
        <div className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-teal-600 text-sm font-bold text-white">L</span>
          <span className="font-semibold">Ledgerly</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <span>Help</span>
          <span className="grid h-8 w-8 place-items-center rounded-full bg-amber-200 text-xs font-semibold text-amber-900">MR</span>
        </div>
      </header>

      <div className="mx-auto flex max-w-6xl gap-10 px-8 py-10">
        <aside className="w-52 shrink-0">
          <h1 className="mb-4 text-xl font-semibold">Settings</h1>
          <nav className="flex flex-col gap-1 text-sm">
            {nav.map((item) => (
              <span key={item} className={item === 'Profile'
                ? 'rounded-md bg-teal-50 px-3 py-2 font-medium text-teal-800'
                : 'rounded-md px-3 py-2 text-slate-600'}>{item}</span>
            ))}
          </nav>
        </aside>

        <main className="flex-1 space-y-6">
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-base font-semibold">Profile</h2>
            <p className="mt-1 text-sm text-slate-500">This is how others see you on Ledgerly.</p>
            <div className="mt-5 flex items-center gap-4">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-amber-200 text-lg font-semibold text-amber-900">MR</span>
              <span className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700">Change photo</span>
              <span className="text-sm text-slate-500">JPG or PNG, up to 2 MB.</span>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-5">
              <Field label="First name" value="Maya" />
              <Field label="Last name" value="Reyes" />
              <Field label="Email" value="maya@example.com" hint="We send receipts and alerts here." wide />
            </div>
            <div className="mt-6 flex justify-end gap-3 border-t border-slate-100 pt-5">
              <span className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600">Cancel</span>
              <span className="rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white shadow-sm">Save changes</span>
            </div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-base font-semibold">Email notifications</h2>
            <ul className="mt-4 divide-y divide-slate-100">
              {toggles.map((t) => (
                <li key={t.label} className="flex items-center justify-between py-3.5">
                  <div>
                    <p className="text-sm font-medium">{t.label}</p>
                    <p className="text-sm text-slate-500">{t.hint}</p>
                  </div>
                  <Toggle on={t.on} />
                </li>
              ))}
            </ul>
          </section>
        </main>
      </div>
    </div>
  )
}
