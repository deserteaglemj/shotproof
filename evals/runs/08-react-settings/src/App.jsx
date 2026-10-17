import { useState } from 'react'

// Font in the shot looks like Inter / system UI sans; Tailwind's default sans stack is used.
const navItems = ['Profile', 'Account', 'Notifications', 'Billing', 'Team', 'Integrations']

const focus = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600'

function Header() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-8">
      <a href="#" className={`flex items-center gap-2.5 rounded-md ${focus}`}>
        <span className="flex size-7 items-center justify-center rounded-md bg-teal-600 text-sm font-bold text-white" aria-hidden="true">L</span>
        <span className="text-base font-semibold text-slate-900">Ledgerly</span>
      </a>
      <div className="flex items-center gap-3">
        <a href="#" className={`rounded text-sm text-slate-600 hover:text-slate-900 ${focus}`}>Help</a>
        <button type="button" aria-label="Account menu" className={`flex size-8 items-center justify-center rounded-full bg-amber-200 text-xs font-semibold text-amber-900 ${focus}`}>MR</button>
      </div>
    </header>
  )
}

function Sidebar() {
  return (
    <aside>
      <h1 className="text-xl font-semibold text-slate-900">Settings</h1>
      <nav aria-label="Settings" className="mt-4">
        <ul className="flex flex-col gap-1">
          {navItems.map((item, i) => (
            <li key={item}>
              <a
                href="#"
                aria-current={i === 0 ? 'page' : undefined}
                className={`flex h-9 items-center rounded-md px-3 text-sm ${focus} ${i === 0 ? 'bg-teal-50 font-medium text-teal-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
              >
                {item}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}

function Card({ children, ...props }) {
  return <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" {...props}>{children}</section>
}

function Field({ id, label, defaultValue, type = 'text', hint }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-slate-700">{label}</label>
      <input
        id={id}
        type={type}
        defaultValue={defaultValue}
        aria-describedby={hint ? `${id}-hint` : undefined}
        className="mt-1.5 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-teal-600 focus:outline-2 focus:outline-teal-600/30"
      />
      {hint && <p id={`${id}-hint`} className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  )
}

function ProfileCard() {
  return (
    <Card aria-labelledby="profile-title">
      <h2 id="profile-title" className="text-base font-semibold text-slate-900">Profile</h2>
      <p className="mt-1 text-sm text-slate-500">This is how others see you on Ledgerly.</p>
      <div className="mt-5 flex items-center gap-4">
        <span className="flex size-16 items-center justify-center rounded-full bg-amber-200 text-lg font-semibold text-amber-900" aria-hidden="true">MR</span>
        <button type="button" className={`h-[34px] rounded-md border border-slate-300 bg-white px-3 text-sm font-medium whitespace-nowrap text-slate-700 hover:bg-slate-50 ${focus}`}>Change photo</button>
        <span className="text-sm text-slate-500">JPG or PNG, up to 2 MB.</span>
      </div>
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
          <Field id="first-name" label="First name" defaultValue="Maya" />
          <Field id="last-name" label="Last name" defaultValue="Reyes" />
        </div>
        <div className="mt-5">
          <Field id="email" label="Email" type="email" defaultValue="maya@example.com" hint="We send receipts and alerts here." />
        </div>
        <div className="mt-6 flex justify-end gap-3 border-t border-slate-100 pt-5">
          <button type="reset" className={`h-9 rounded-md px-4 text-sm font-medium text-slate-700 hover:bg-slate-100 ${focus}`}>Cancel</button>
          <button type="submit" className={`h-9 rounded-md bg-teal-600 px-4 shadow-sm whitespace-nowrap text-sm font-semibold text-white hover:bg-teal-700 ${focus}`}>Save changes</button>
        </div>
      </form>
    </Card>
  )
}

function Toggle({ label, initial }) {
  const [on, setOn] = useState(initial)
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      aria-label={label}
      onClick={() => setOn(!on)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${on ? 'bg-teal-600' : 'bg-slate-300'} ${focus}`}
    >
      <span className={`absolute top-0.5 left-0.5 size-5 rounded-full bg-white shadow transition-transform ${on ? 'translate-x-5' : ''}`} />
    </button>
  )
}

const notifications = [
  { title: 'Weekly summary', desc: "A short email every Monday with last week's activity.", on: true },
  { title: 'Mentions', desc: 'Tell me when someone mentions me in a comment.', on: true },
  { title: 'Product updates', desc: 'New features and changes, about once a month.', on: false },
]

function NotificationsCard() {
  return (
    <Card aria-labelledby="notif-title">
      <h2 id="notif-title" className="text-base font-semibold text-slate-900">Email notifications</h2>
      <ul className="mt-4 divide-y divide-slate-100">
        {notifications.map((n) => (
          <li key={n.title} className="flex items-center justify-between gap-4 py-3.5">
            <div>
              <p className="text-sm font-medium text-slate-900">{n.title}</p>
              <p className="text-sm text-slate-500">{n.desc}</p>
            </div>
            <Toggle label={n.title} initial={n.on} />
          </li>
        ))}
      </ul>
    </Card>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <Header />
      <main className="mx-auto grid max-w-[1088px] grid-cols-1 gap-10 px-4 py-10 md:grid-cols-[208px_1fr] md:px-0">
        <Sidebar />
        <div className="flex min-w-0 flex-col gap-6">
          <ProfileCard />
          <NotificationsCard />
        </div>
      </main>
    </div>
  )
}
