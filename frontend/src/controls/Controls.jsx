function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  )
}

export default function Controls({ values, onChange }) {
  const set = (key) => (e) => onChange({ ...values, [key]: e.target.value })

  return (
    <form className="controls" onSubmit={(e) => e.preventDefault()}>
      <Field label="Delivery day">
        <input type="date" value={values.date} onChange={set('date')} required />
      </Field>
      <Field label="Cutoff on the day before (UTC)">
        <input type="time" value={values.cutoff} onChange={set('cutoff')} required />
      </Field>
      <Field label="Accuracy from">
        <input type="date" value={values.dateFrom} onChange={set('dateFrom')} required />
      </Field>
      <Field label="Accuracy to">
        <input type="date" value={values.dateTo} onChange={set('dateTo')} required />
      </Field>
    </form>
  )
}