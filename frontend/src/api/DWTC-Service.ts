import Api from '@/api/api'

export default {
    getDWTV(params: { dwtcId: number }): Promise<any> {
        return Promise.resolve("<tbody>\n <tr> \n" +
            "  <th>1-Month</th> \n" +
            "  <td class=\"first up\">+1.38%</td> \n" +
            "  <th class=\"last\">1-Year</th> \n" +
            "  <td class=\"last up\">+8.88%</td> \n" +
            " </tr> \n" +
            " <tr> \n" +
            "  <th>3-Month</th> \n" +
            "  <td class=\"first up\">+3.72%</td> \n" +
            "  <th class=\"last\">3-Year</th> \n" +
            "  <td class=\"last up\">+1.26%</td> \n" +
            " </tr> \n" +
            " <tr> \n" +
            "  <th>Year To Date</th> \n" +
            "  <td class=\"first up\">+15.98%</td> \n" +
            "  <th class=\"last\">5-Year</th> \n" +
            "  <td class=\"last\">-</td> \n" +
            " </tr> \n" +
            " <tr> \n" +
            "  <th>Expense Ratio</th> \n" +
            "  <td class=\"first\">-</td> \n" +
            "  <th class=\"last\"></th> \n" +
            "  <td class=\"last\"></td> \n" +
            " </tr> \n" +
            "</tbody>");
        // return Api().get('/dwtc/' + params.dwtcId);
    }
}