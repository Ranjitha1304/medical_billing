let cart = JSON.parse(localStorage.getItem('cart') || '[]');

function renderCart() {
    const tbody = document.getElementById('cart-items');
    tbody.innerHTML = '';
    let total = 0;

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;

        tbody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${item.name}</td>
                <td>${item.batch_no}</td>
                <td>₹${item.price}</td>
                <td>
                    <button onclick="changeQty(${index}, -1)">-</button>
                    ${item.quantity}
                    <button onclick="changeQty(${index}, 1)">+</button>
                </td>
                <td>₹${subtotal.toFixed(2)}</td>
                <td><button onclick="removeItem(${index})">🗑</button></td>
            </tr>
        `;
    });

    const discount = parseFloat(document.getElementById('discount').value || 0);
    const final = total - (total * discount / 100);
    const rounded = Math.round(final);

    document.getElementById('final-total').innerText = final.toFixed(2);
    document.getElementById('rounded-total').innerText = rounded;
    document.getElementById('cart-data').value = JSON.stringify(cart);

        // Keep localStorage updated
    localStorage.setItem('cart', JSON.stringify(cart));
}

function changeQty(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    renderCart();
}

function removeItem(index) {
    cart.splice(index, 1);
    renderCart();
}

document.getElementById('discount').addEventListener('input', renderCart);

renderCart();

document.querySelector('form').addEventListener('submit', function () {
    localStorage.removeItem('cart');
});
