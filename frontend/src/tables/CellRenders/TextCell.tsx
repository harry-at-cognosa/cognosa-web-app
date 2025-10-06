interface Props {
  value: boolean;
}

export default function TextCell({ value }: Props) {
  return (
    <textarea className="form-control" rows={5}>
      {value}
    </textarea>
  );
}
