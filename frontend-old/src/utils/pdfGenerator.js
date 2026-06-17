import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generateReceipt = (data) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(22);
  doc.setTextColor(37, 99, 235); // Primary color
  doc.text('MoroGo', 14, 20);
  
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text('Le meilleur du voyage au Maroc', 14, 28);
  doc.text(`Date : ${new Date().toLocaleDateString('fr-FR')}`, 140, 20);
  doc.text(`Reçu N° : ${Math.floor(Math.random() * 1000000)}`, 140, 26);
  
  // Title
  doc.setFontSize(16);
  doc.setTextColor(30);
  doc.text('Reçu de Paiement', 105, 45, null, null, 'center');
  
  // Customer Info
  doc.setFontSize(12);
  doc.text(`Client : ${data.customerName || 'Client'}`, 14, 60);
  doc.text(`Service : ${data.service === 'taxi' ? 'Transport Privé' : 'Hébergement'}`, 14, 68);
  
  if (data.service === 'taxi') {
    doc.autoTable({
      startY: 80,
      head: [['Détails du Trajet', 'Information']],
      body: [
        ['Départ', data.pickup],
        ['Destination', data.destination],
        ['Véhicule', data.vehicle_category],
        ['Code Confirmation', data.confirmation_code],
      ],
      theme: 'grid',
      headStyles: { fillColor: [37, 99, 235] }
    });
  } else if (data.service === 'hotel') {
    doc.autoTable({
      startY: 80,
      head: [['Détails de la Réservation', 'Information']],
      body: [
        ['Hôtel', data.hotelName],
        ['Dates', `${data.checkIn} au ${data.checkOut}`],
        ['Nombre de nuits', data.nights],
        ['Nombre de personnes', data.guests],
      ],
      theme: 'grid',
      headStyles: { fillColor: [37, 99, 235] }
    });
  }

  // Total
  const finalY = doc.lastAutoTable.finalY || 80;
  doc.setFontSize(14);
  doc.setTextColor(0);
  doc.text(`Montant Payé : ${data.amount} MAD`, 140, finalY + 15);
  
  // Footer
  doc.setFontSize(10);
  doc.setTextColor(150);
  doc.text('Merci pour votre confiance.', 105, 280, null, null, 'center');
  doc.text('MoroGo - Contact: support@morogo.ma', 105, 286, null, null, 'center');

  // Download
  doc.save(`Recu_MoroGo_${data.service}_${new Date().getTime()}.pdf`);
};
