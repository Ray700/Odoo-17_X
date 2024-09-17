/** @odoo-module **/

import { Component } from '@odoo/owl';
import { useState } from '@odoo/owl/hooks';
import { rpc } from 'web.rpc';
import { patch } from 'web.utils';

class DashboardComponent extends Component {
    // Define component template
    static template = "customer_dashboard.dashboard_component";

    // State to store data
    state = useState({
        deliveries: [],
        payments: [],
    });

    // Lifecycle hook to fetch data on component mount
    async willStart() {
        const dashboardData = await rpc.query({
            route: '/dashboard/data',
        });
        this.state.deliveries = dashboardData.deliveries;
        this.state.payments = dashboardData.payments;
    }
    
    // Bar chart rendering for payments
    getTotalPayments() {
        const payments = this.state.payments;
        const labels = payments.map(p => p.date);
        const data = payments.map(p => p.amount);

        new Chart(this.el.querySelector('#paymentChart'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Payments (Daily)',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            }
        });
    }
}
DashboardComponent.template = 'customer_dashboard.dashboard_component';

// Register the component in the web client
patch(DashboardComponent, "customer_dashboard", {
    mounted() {
        this.getTotalPayments();
    }
});

export default DashboardComponent;
