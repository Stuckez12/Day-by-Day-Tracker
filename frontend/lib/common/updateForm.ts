export function updateForm<T extends Record<string, any>>(
  e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  form: T,
  setForm: React.Dispatch<React.SetStateAction<T>>,
  // form: T,
  // setForm: (value: T) => void,
) {
  const { name, value } = e.target;
  setForm({
    ...form,
    [name]: value,
  });
}
