import sys

file_path = '/home/ubuntu/apps/zolu-kas/app/dashboard/page.tsx'

with open(file_path, 'r') as f:
    content = f.read()

# Replace Add logic
content = content.replace(
    '    if (!formAmount || parseFloat(formAmount) <= 0) {',
    '    const rawAmount = parseFloat(formAmount.replace(/,/g, \'\'));\n    if (!formAmount || isNaN(rawAmount) || rawAmount <= 0) {'
)
content = content.replace(
    '          amount: parseFloat(formAmount),',
    '          amount: rawAmount,'
)

# Replace Add input field
content = content.replace(
    '''                <input
                  type="number"
                  required
                  min="1"
                  step="any"
                  value={formAmount}
                  onChange={(e) => setFormAmount(e.target.value)}
                  placeholder="Contoh: 50000"''',
    '''                <input
                  type="text"
                  inputMode="numeric"
                  required
                  value={formAmount}
                  onChange={(e) => {
                    const raw = e.target.value.replace(/[^0-9]/g, '');
                    setFormAmount(raw ? parseInt(raw, 10).toLocaleString('en-US') : '');
                  }}
                  placeholder="Contoh: 50,000"'''
)

# Replace Edit input field
content = content.replace(
    '''                <input
                  type="number"
                  required
                  min="1"
                  step="any"
                  value={editingTx.amount}
                  onChange={(e) => setEditingTx({ ...editingTx, amount: parseFloat(e.target.value) || 0 })}''',
    '''                <input
                  type="text"
                  inputMode="numeric"
                  required
                  value={editingTx.amount ? editingTx.amount.toLocaleString('en-US') : ''}
                  onChange={(e) => {
                    const raw = e.target.value.replace(/[^0-9]/g, '');
                    setEditingTx({ ...editingTx, amount: raw ? parseInt(raw, 10) : 0 });
                  }}'''
)

with open(file_path, 'w') as f:
    f.write(content)

print('Success')
