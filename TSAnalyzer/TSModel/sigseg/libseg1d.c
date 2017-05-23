#include <stdio.h>
#include <stdlib.h>
#include <math.h> /*FIX ME*/
#define MAX(A,B) (A-B)>0?A:B
#define MIN(A,B) (A-B)<0?A:B
#define LINELENGTH 80
#define LINEL 80

typedef struct
{
    /* 2 indexes SUM_ij
     *
     *
     * (L=left, C=center, R=right)
     *
     * 0<i<n --> 3 combinations, n-2 points
     *
     *    i  +
     *          /|\
     *             / | \
     *        j   +  +  +
     *           -1  0  +1
     *            L  C   R
     *
     * i=0 --> 2 combinations, 1 point
     *
     *    i  +
     *           |\
     *               | \
     *        j      +  +
     *               0  +1
     *               C   R
     *
     *
     * i=n  --> 2 combinations, 1 point
     *
     *    i      +
     *          /|
     *             / |
     *        j   +  +
     *           -1  0
     *            L  C
     *
    */
    double *pp;                /* beta & (alpha-beta) & (u-g)^2 */
    double *ppd;               /* beta & (alpha-beta) */
    double *f11, *f12, *f22;       /* (u-g)^2 */
    double *pf1, *pf2;         /* (u-g)^2 */
    double *f11dd, *f12dd, *f22dd; /* lambda_epsilon */

    /* 4 indexes SUM_ijhk
     *
     * (L=left, C=center, R=right)
     *
     * 0<i<n --> 15 combinations, n-1 points
     *
     *   i        +   +   +   +   +   +   +  +  +   +   +   +   +   +   +
     *       /   /   /   /    |   |   |  |  |   |   |    \   \   \   \
     *   j      +   +   +   +     +   +   +  +  +   +   +     +   +   +   +
     *      |   |    \   \   /   /    |  |  |    \   \   /   /    |   |
     *   h      +   +     +   + *   +     +  +  +     +   + +   +     +   +
     *      |    \   /    | |    \   /   |   \   /    | |    \   /    |
     *   k      +     + +     + +     + +    +    + +     + +     + +     +
     *          L C L C L C L C L C L C L C  C  C R C R C R C R C R C R C R
     *
     *       1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
     *
     * i=0   --> 8 combinations (8 to 15, see the schema above), 1 point
     *
     * i=n   --> 8 combinations (1 to 8, see the schema above), 1 point
     *
    */
    double *ppf11d, *ppf12d, *ppf22d;    /*mu_epsilon*/
    double *ppf11dd, *ppf12dd, *ppf22dd; /*first 3 SUMs --- gamma*/
}
shp_fun_int; /* Shape functions integrals */


typedef struct
{
    int *i;
    int *j;
    int *h;
    int *k;
}
pos_idx_jhk; /* Given the shape function combination it gives the position indexes for the three indexes summations */


typedef struct
{
    double *u1;  /* The function u that approximates the given data */
    double *u2;  /* The first derivative of the funtion u */
    double *s;   /* The discontinuity function s */
    double *sgm; /* The discntinuity function sigma */
}
appx_u_s_sigma; /* The functional's functions */


typedef struct
{
    double alpha;
    double beta;
    double epsilon;
    double gamma;       /* gamma */
    double lambda_eps;  /* delta_epsilon */
    double mu_eps;      /* mu_epsilon */
    double tol;
    int mx_iter;
}
func_params; /* The functional parameters (or weights). */


typedef struct
{
    int *j; /* Combination re-indexing for j fix sommatories */
    int *h; /* Combination re-indexing for h fix sommatories */
    int *k; /* Combination re-indexing for k fix sommatories */
}
combs; /* True combinations for Sd_4 terms
        * Combinations re-indexing is not needed for sommatories with fixed index "i"
    * since the original combinations can be used */


int setup(shp_fun_int *sfi, int n, pos_idx_jhk *pos)
{
    /* 2 indexes shape functions */
    sfi->pp[0] = 1./(3. * n); /* -2 --- right corner */
    sfi->pp[1] = 1./(6. * n); /* -1 --- j=i-1 */
    sfi->pp[2] = 2./(3. * n); /*  0 --- j=i   */
    sfi->pp[3] = 1./(6. * n); /* +1 --- j=i+1 */
    sfi->pp[4] = 1./(3. * n); /* +2 --- left corner */

    sfi->ppd[0] =  1. * n; /* -2 --- right corner */
    sfi->ppd[1] = -1. * n; /* -1 --- j=i-1 */
    sfi->ppd[2] =  2. * n; /*  0 --- j=i   */
    sfi->ppd[3] = -1. * n; /* +1 --- j=i+1 */
    sfi->ppd[4] =  1. * n; /* +2 --- left corner */

    sfi->f11[0] = 13./(35. * n); /* -2 --- right corner */
    sfi->f11[1] =  9./(70. * n); /* -1 --- j=i-1 */
    sfi->f11[2] = 26./(35. * n); /*  0 --- j=i   */
    sfi->f11[3] =  9./(70. * n); /* +1 --- j=i+1 */
    sfi->f11[4] = 13./(35. * n); /* +2 --- left corner */

    sfi->f12[0] = -11./(210. * n*n); /* -2 --- right corner */
    sfi->f12[1] =  13./(420. * n*n); /* -1 --- j=i-1 */
    sfi->f12[2] =   0.; /*  0 --- j=i   */
    sfi->f12[3] = -13./(420. * n*n) ; /* +1 --- j=i+1 */
    sfi->f12[4] =  11./(210. * n*n); /* +2 --- left corner */

    sfi->f22[0] =  1./(105. * n*n*n); /* -2 --- right corner */
    sfi->f22[1] = -1./(140. * n*n*n); /* -1 --- j=i-1 */
    sfi->f22[2] =  2./(105. * n*n*n); /*  0 --- j=i   */
    sfi->f22[3] = -1./(140. * n*n*n); /* +1 --- j=i+1 */
    sfi->f22[4] =  1./(105. * n*n*n); /* +2 --- left corner */

    sfi->pf1[0] = 7./(20. * n); /* -2 --- right corner */
    sfi->pf1[1] = 3./(20. * n); /* -1 --- j=i-1 */
    sfi->pf1[2] = 7./(10. * n); /*  0 --- j=i   */
    sfi->pf1[3] = 3./(20. * n); /* +1 --- j=i+1 */
    sfi->pf1[4] = 7./(20. * n); /* +2 --- left corner */

    sfi->pf2[0] = -1./(20. * n*n); /* -2 --- right corner */
    sfi->pf2[1] =  1./(30. * n*n); /* -1 --- j=i-1 */
    sfi->pf2[2] =  0.; /*  0 --- j=i   */
    sfi->pf2[3] = -1./(30. * n*n); /* +1 --- j=i+1 */
    sfi->pf2[4] =  1./(20. * n*n); /* +2 --- left corner */

    sfi->f11dd[0] =  12. * n*n*n; /* -2 --- right corner */
    sfi->f11dd[1] = -12. * n*n*n; /* -1 --- j=i-1 */
    sfi->f11dd[2] =  24. * n*n*n; /*  0 --- j=i   */
    sfi->f11dd[3] = -12. * n*n*n; /* +1 --- j=i+1 */
    sfi->f11dd[4] =  12. * n*n*n; /* +2 --- left corner */

    sfi->f12dd[0] = -6. * n*n; /* -2 --- right corner */
    sfi->f12dd[1] = -6. * n*n; /* -1 --- j=i-1 */
    sfi->f12dd[2] =  0.; /*  0 --- j=i   */
    sfi->f12dd[3] =  6. * n*n; /* +1 --- j=i+1 */
    sfi->f12dd[4] =  6. * n*n; /* +2 --- left corner */

    sfi->f22dd[0] = 4. * n; /* -2 --- right corner */
    sfi->f22dd[1] = 2. * n; /* -1 --- j=i-1 */
    sfi->f22dd[2] = 8. * n; /*  0 --- j=i   */
    sfi->f22dd[3] = 2. * n; /* +1 --- j=i+1 */
    sfi->f22dd[4] = 4. * n; /* +2 --- left corner */


    /* 4 indexes shape functions */
    sfi->ppf11d[0] =  12./35. * n; /* -8 --- right corner */
    sfi->ppf11d[1] =   9./35. * n; /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf11d[2] =  -9./35. * n; /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf11d[3] =  -9./35. * n; /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf11d[4] =   9./35. * n; /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf11d[5] =  12./35. * n; /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf11d[6] = -12./35. * n; /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf11d[7] = -12./35. * n; /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf11d[8] =  24./35. * n; /*  0 --- j=i   h=i   k=i   */
    sfi->ppf11d[9] = -12./35. * n; /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf11d[10] = -12./35. * n; /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf11d[11] =  12./35. * n; /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf11d[12] =   9./35. * n; /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf11d[13] =  -9./35. * n; /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf11d[14] =  -9./35. * n; /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf11d[15] =   9./35. * n; /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf11d[16] =  12./35. * n; /* +8 --- left corner */

    sfi->ppf12d[0] = 1./35.; /* -8 --- right corner */
    sfi->ppf12d[1] =  1./35.; /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf12d[2] =  1./35.; /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf12d[3] = -1./35.; /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf12d[4] = -1./35.; /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf12d[5] =  1./14.; /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf12d[6] = -1./35.; /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf12d[7] = -1./14.; /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf12d[8] =  0.; /*  0 --- j=i   h=i   k=i   */
    sfi->ppf12d[9] =  1./14.; /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf12d[10] = 1./35.; /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf12d[11] = -1./14.; /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf12d[12] =  1./35.; /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf12d[13] =  1./35.; /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf12d[14] = -1./35.; /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf12d[15] = -1./35.; /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf12d[16] = -1./35.; /* +8 --- left corner */

    sfi->ppf22d[0] =  3./(35. * n); /* -8 --- right corner */
    sfi->ppf22d[1] =  1./(70. * n); /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf22d[2] = -1./(420. * n); /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf22d[3] = -1./(420. * n); /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf22d[4] =  1./(70. * n); /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf22d[5] =  2./(105. * n); /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf22d[6] = -1./(70. * n); /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf22d[7] = -1./(70. * n); /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf22d[8] =  6./(35. * n); /*  0 --- j=i   h=i   k=i   */
    sfi->ppf22d[9] = -1./(70. * n); /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf22d[10] = -1./(70. * n); /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf22d[11] =  2./(105. * n); /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf22d[12] =  1./(70. * n); /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf22d[13] = -1./(420. * n); /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf22d[14] = -1./(420. * n); /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf22d[15] =  1./(70. * n); /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf22d[16] =  3./(35. * n); /* +8 --- left corner */

    sfi->ppf11dd[0] =  24./5. * n*n*n; /* -8 --- right corner */
    sfi->ppf11dd[1] =   6./5. * n*n*n; /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf11dd[2] =  -6./5. * n*n*n; /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf11dd[3] =  -6./5. * n*n*n; /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf11dd[4] =   6./5. * n*n*n; /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf11dd[5] =  24./5. * n*n*n; /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf11dd[6] = -24./5. * n*n*n; /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf11dd[7] = -24./5. * n*n*n; /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf11dd[8] =  48./5. * n*n*n; /*  0 --- j=i   h=i   k=i   */
    sfi->ppf11dd[9] = -24./5. * n*n*n; /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf11dd[10] = -24./5. * n*n*n; /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf11dd[11] =  24./5. * n*n*n; /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf11dd[12] =   6./5. * n*n*n; /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf11dd[13] =  -6./5. * n*n*n; /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf11dd[14] =  -6./5. * n*n*n; /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf11dd[15] =   6./5. * n*n*n; /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf11dd[16] =  24./5. * n*n*n; /* +8 --- left corner */

    sfi->ppf12dd[0] = -17./5. * n*n; /* -8 --- right corner */
    sfi->ppf12dd[1] =   3./5. * n*n; /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf12dd[2] =   3./5. * n*n; /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf12dd[3] =  -3./5. * n*n; /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf12dd[4] =  -3./5. * n*n; /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf12dd[5] =   7./5. * n*n; /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf12dd[6] =  17./5. * n*n; /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf12dd[7] =  -7./5. * n*n; /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf12dd[8] =   0.; /*  0 --- j=i   h=i   k=i   */
    sfi->ppf12dd[9] =   7./5. * n*n; /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf12dd[10] = -17./5. * n*n; /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf12dd[11] =  -7./5. * n*n; /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf12dd[12] =   3./5. * n*n; /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf12dd[13] =   3./5. * n*n; /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf12dd[14] =  -3./5. * n*n; /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf12dd[15] =  -3./5. * n*n; /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf12dd[16] = 17./5. * n*n; /* +8 --- left corner */

    sfi->ppf22dd[0] = 38./15. * n; /* -8 --- right corner */
    sfi->ppf22dd[1] =  7./15. * n; /* -7 --- j=i-1 h=i-1 k=i-1 */
    sfi->ppf22dd[2] =  2./15. * n; /* -6 --- j=i-1 h=i-1 k=i   */
    sfi->ppf22dd[3] =  2./15. * n; /* -5 --- j=i-1 h=i   k=i-1 */
    sfi->ppf22dd[4] =  7./15. * n; /* -4 --- j=i-1 h=i   k=i   */
    sfi->ppf22dd[5] =  8./15. * n; /* -3 --- j=i   h=i-1 k=i-1 */
    sfi->ppf22dd[6] = 13./15. * n; /* -2 --- j=i   h=i-1 k=i   */
    sfi->ppf22dd[7] = 13./15. * n; /* -1 --- j=i   h=i   k=i-1 */
    sfi->ppf22dd[8] = 76./15. * n; /*  0 --- j=i   h=i   k=i   */
    sfi->ppf22dd[9] = 13./15. * n; /* +1 --- j=i   h=i   k=i+1 */
    sfi->ppf22dd[10] = 13./15. * n; /* +2 --- j=i   h=i+1 k=i   */
    sfi->ppf22dd[11] =  8./15. * n; /* +3 --- j=i   h=i+1 k=i+1 */
    sfi->ppf22dd[12] =  7./15. * n; /* +4 --- j=i+1 h=i   k=i   */
    sfi->ppf22dd[13] =  2./15. * n; /* +5 --- j=i+1 h=i   k=i+1 */
    sfi->ppf22dd[14] =  2./15. * n; /* +6 --- j=i+1 h=i+1 k=i   */
    sfi->ppf22dd[15] =  7./15. * n; /* +7 --- j=i+1 h=i+1 k=i+1 */
    sfi->ppf22dd[16] = 38./15. * n; /* +8 --- left corner */


    /* Position indexe from configuration index for 4 indexes summations */
    pos->i[0] =  0;
    pos->j[0] =  0;
    pos->h[0] =  0;
    pos->k[0] =  0;

    pos->i[1] =  0;
    pos->j[1] = -1;
    pos->h[1] = -1;
    pos->k[1] = -1;

    pos->i[2] =  0;
    pos->j[2] = -1;
    pos->h[2] = -1;
    pos->k[2] =  0;

    pos->i[3] =  0;
    pos->j[3] = -1;
    pos->h[3] =  0;
    pos->k[3] = -1;

    pos->i[4] =  0;
    pos->j[4] = -1;
    pos->h[4] =  0;
    pos->k[4] =  0;

    pos->i[5] =  0;
    pos->j[5] =  0;
    pos->h[5] = -1;
    pos->k[5] = -1;

    pos->i[6] =  0;
    pos->j[6] =  0;
    pos->h[6] = -1;
    pos->k[6] =  0;

    pos->i[7] =  0;
    pos->j[7] =  0;
    pos->h[7] =  0;
    pos->k[7] = -1;

    pos->i[8] =  0;
    pos->j[8] =  0;
    pos->h[8] =  0;
    pos->k[8] =  0;

    pos->i[9] =  0;
    pos->j[9] =  0;
    pos->h[9] =  0;
    pos->k[9] =  1;

    pos->i[10] =  0;
    pos->j[10] =  0;
    pos->h[10] =  1;
    pos->k[10] =  0;

    pos->i[11] =  0;
    pos->j[11] =  0;
    pos->h[11] =  1;
    pos->k[11] =  1;

    pos->i[12] =  0;
    pos->j[12] =  1;
    pos->h[12] =  0;
    pos->k[12] =  0;

    pos->i[13] =  0;
    pos->j[13] =  1;
    pos->h[13] =  0;
    pos->k[13] =  1;

    pos->i[14] =  0;
    pos->j[14] =  1;
    pos->h[14] =  1;
    pos->k[14] =  0;

    pos->i[15] =  0;
    pos->j[15] =  1;
    pos->h[15] =  1;
    pos->k[15] =  1;

    pos->i[16] =  0;
    pos->j[16] =  0;
    pos->h[16] =  0;
    pos->k[16] =  0;

    return (0);
}



/* ========================================================================= */


/* Minimizations of the entire functioal */
int minimize(double *g_in ,int np, func_params prm, appx_u_s_sigma *apx, shp_fun_int *sfi, pos_idx_jhk pos, double *mx_diff)
{
    combs TC;
    int *TC_j;

    /* Memory allocation and initialization of the true combinations */
    /* TC.i is not needed because it's a simple increment from 0 to 16. TC.i corresponds to the definition of the reference combinations */
    TC.j=malloc(17 * sizeof(int));
    TC.h=malloc(17 * sizeof(int));
    TC.k=malloc(17 * sizeof(int));

    TC.j[0]=0;
    TC.j[1]=12;
    TC.j[2]=13;
    TC.j[3]=14;
    TC.j[4]=15;
    TC.j[5]=5;
    TC.j[6]=6;
    TC.j[7]=7;
    TC.j[8]=8;
    TC.j[9]=9;
    TC.j[10]=10;
    TC.j[11]=11;
    TC.j[12]=1;
    TC.j[13]=2;
    TC.j[14]=3;
    TC.j[15]=4;
    TC.j[16]=16;

    TC.h[0]=0;
    TC.h[1]=10;
    TC.h[2]=3;
    TC.h[3]=14;
    TC.h[4]=7;
    TC.h[5]=11;
    TC.h[6]=4;
    TC.h[7]=15;
    TC.h[8]=8;
    TC.h[9]=1;
    TC.h[10]=12;
    TC.h[11]=5;
    TC.h[12]=9;
    TC.h[13]=2;
    TC.h[14]=13;
    TC.h[15]=6;
    TC.h[16]=16;

    TC.k[0]=0;
    TC.k[1]=9;
    TC.k[2]=2;
    TC.k[3]=13;
    TC.k[4]=6;
    TC.k[5]=11;
    TC.k[6]=4;
    TC.k[7]=15;
    TC.k[8]=8;
    TC.k[9]=1;
    TC.k[10]=12;
    TC.k[11]=5;
    TC.k[12]=10;
    TC.k[13]=3;
    TC.k[14]=14;
    TC.k[15]=7;
    TC.k[16]=16;


    TC_j=malloc(5 * sizeof(int));

    TC_j[0]=0;
    TC_j[1]=3;
    TC_j[2]=2;
    TC_j[3]=1;
    TC_j[4]=4;


    /* Minimization of the functional's function u */
    if (minimize_u1(g_in, np, prm, apx, sfi, pos, TC, TC_j, mx_diff) != 0)
        return (-1);

    /* Minimization of the functional's function u' */
    if (minimize_u2(g_in, np, prm, apx, sfi, pos, TC, TC_j) != 0)
        return (-2);

    /* Minimization of the functional's function s */
    if (minimize_s(g_in, np, prm, apx, sfi, pos, TC, TC_j) != 0)
        return (-3);

    /* Minimization of the functional's function sigma */
    if (minimize_sgm(g_in, np, prm, apx, sfi, pos, TC, TC_j) != 0)
        return (-4);


    /* Free allocated memory */
    free(TC.j);
    free(TC.h);
    free(TC.k);
    free(TC_j);


    return (0);
}



/* ========================================================================= */
/* Minimization of the functional's function u */
/* ========================================================================= */
int minimize_u1(double *g_in ,int np, func_params prm, appx_u_s_sigma *apx, shp_fun_int *sfi, pos_idx_jhk pos, combs TC, int *TC_j, double *mx_diff)
{
    int l; /* Point position counter. It is not i to keep the counter distinguisced by the position index */
    double old_u1=0.;
    double num=0., den=1.;

    int c, m, tc_i, tc_j, tc_h, tc_k; /* Combinations index, combination counter, truecombinations indexes */
    double S_2=0., S_4=0.;
    double Sd_2=0., Sd_4=0.;

    double u1_f11dd=0., u2_f12dd=0., u1_f11=0., u2_f12, g_pf1=0.;
    double s_s_u1_ppf11dd=0., s_s_u2_ppf12dd=0., sgm_sgm_u1_ppf11d=0., sgm_sgm_u2_ppf12d=0.;
    double s_s_ppf11dd=0., sgm_sgm_ppf11d=0.;


    /* First point */
    l = 0;

    old_u1 = apx->u1[l];
    for (m = 3; m <= 4 ; m++)
    {
        tc_i=m;
        tc_j=TC_j[m];

        u1_f11dd = apx->u1[l-(m-4)] * sfi->f11dd[tc_j];
        u2_f12dd = apx->u2[l-(m-4)] * sfi->f12dd[tc_i];
        u1_f11 = apx->u1[l-(m-4)] * sfi->f11[tc_j];
        u2_f12 = apx->u2[l-(m-4)] * sfi->f12[tc_i];
        g_pf1 = g_in[l-(m-4)] * sfi->pf1[tc_j];
        S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f11dd + u2_f12dd) + 2. * (u1_f11 + u2_f12 - g_pf1);
    }

    c = 4;
    Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f11dd[c] + 2. * sfi->f11[c];

    /* In the following, TC is used because the order is relevant */
    for (m = 9; m <= 16; m++)
    {
        tc_h=TC.h[m];
        tc_k=TC.k[m];

        s_s_u1_ppf11dd = apx->s[l+pos.i[tc_k]-pos.k[tc_k]] * apx->s[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf11dd[tc_k];
        s_s_u2_ppf12dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf12dd[tc_h];
        sgm_sgm_u1_ppf11d = apx->sgm[l+pos.i[tc_k]-pos.k[tc_k]] * apx->sgm[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf11d[tc_k];
        sgm_sgm_u2_ppf12d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf12d[tc_h];
        S_4 += 2. * prm.gamma * (s_s_u1_ppf11dd + s_s_u2_ppf12dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf11d + sgm_sgm_u2_ppf12d);
    }

    /* In the following cases, pos.h[] == pos.k[] since the running combinations are those with h=k=l (i is not equal to l)
     * Only the central part of the combination sequencies (m=5 ... 11) is hence considered.
     * For this set of combinations: TC.h[m] == TC.k[m] --- For simplicity, only the index h is used
     * Since we are now considering the first point, the central part of the combination sequencies reduces to m=9 ... 11 */
    for (m = 9; m <= 11; m++) /* Here m is a counter, the combinations id is given by TC */
    {
        tc_h=TC.h[m];
        s_s_ppf11dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11dd[tc_h];
        sgm_sgm_ppf11d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11d[tc_h];
        Sd_4 += 2. * prm.gamma * s_s_ppf11dd + 2. * prm.mu_eps * sgm_sgm_ppf11d;
    }

    /* Here c is the combinations index (TC.x[16] is equal to 16 for every x, with x=i,j,h,k) */
    c = 16;
    s_s_ppf11dd = apx->s[l+pos.i[c]-pos.h[c]] * apx->s[l+pos.j[c]-pos.h[c]] * sfi->ppf11dd[c];
    sgm_sgm_ppf11d = apx->sgm[l+pos.i[c]-pos.h[c]] * apx->sgm[l+pos.j[c]-pos.h[c]] * sfi->ppf11d[c];
    Sd_4 += 2. * prm.gamma * s_s_ppf11dd + 2. * prm.mu_eps * sgm_sgm_ppf11d;

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    apx->u1[l] = apx->u1[l] - num / den;

    *mx_diff = MAX(*mx_diff, fabs(old_u1 - apx->u1[l]));



    /* Internal points */
    for (l = 1; l <= np-2; l++)
    {
        old_u1 = apx->u1[l];

        S_2=0.;
        S_4=0.;
        Sd_2=0.;
        Sd_4=0.;

        for (c = 1; c <= 3; c++)
        {
            tc_i=c;
            tc_j=TC_j[c];
            u1_f11dd = apx->u1[l+(c-2)] * sfi->f11dd[tc_j];
            u2_f12dd = apx->u2[l+(c-2)] * sfi->f12dd[tc_i];
            u1_f11 = apx->u1[l+(c-2)] * sfi->f11[tc_j];
            u2_f12 = apx->u2[l+(c-2)] * sfi->f12[tc_i];
            g_pf1 = g_in[l+(c-2)] * sfi->pf1[tc_j];

            S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f11dd + u2_f12dd) + 2. * (u1_f11 + u2_f12 - g_pf1);
        }

        c = 2;
        Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f11dd[c] + 2. * sfi->f11[c];

        /* In the following, TC is not needed and c can be used directly as a counter because all the combinations have to be taken into account.
         * This means that the original order of the combinations indexes is not respected without this leading to any problem */
        for (c = 1; c <= 15; c++)
        {
            s_s_u1_ppf11dd = apx->s[l+pos.i[c]-pos.k[c]] * apx->s[l+pos.j[c]-pos.k[c]] * apx->u1[l+pos.h[c]-pos.k[c]] * sfi->ppf11dd[c]; /*gamma*/
            s_s_u2_ppf12dd = apx->s[l+pos.i[c]-pos.h[c]] * apx->s[l+pos.j[c]-pos.h[c]] * apx->u2[l+pos.k[c]-pos.h[c]] * sfi->ppf12dd[c]; /*gamma*/
            sgm_sgm_u1_ppf11d = apx->sgm[l+pos.i[c]-pos.k[c]] * apx->sgm[l+pos.j[c]-pos.k[c]] * apx->u1[l+pos.h[c]-pos.k[c]] * sfi->ppf11d[c]; /*mu_epsilon*/
            sgm_sgm_u2_ppf12d = apx->sgm[l+pos.i[c]-pos.h[c]] * apx->sgm[l+pos.j[c]-pos.h[c]] * apx->u2[l+pos.k[c]-pos.h[c]] * sfi->ppf12d[c]; /*mu_epsilon*/

            S_4 += 2. * prm.gamma * (s_s_u1_ppf11dd + s_s_u2_ppf12dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf11d + sgm_sgm_u2_ppf12d);
        }

        /* In the following cases, pos.h[] == pos.k[] since the running combinations are those with h=k=l (i is not equal to l)
         * Only the central part of the combination sequencies (m=5 ... 11) is hence considered.
         * For this set of combinations: TC.h[m] == TC.k[m] --- For simplicity, only the index h is used */
        for (m = 5; m <= 11; m++) /*here m is a counter and no longer the combinations id which is given by TC*/
        {
        tc_h=TC.h[m];

        s_s_ppf11dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11dd[tc_h]; /*gamma*/
        sgm_sgm_ppf11d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11d[tc_h]; /*mu_epsilon*/

        Sd_4 += 2. * prm.gamma * s_s_ppf11dd + 2. * prm.mu_eps * sgm_sgm_ppf11d;
        }

        num = S_2 + S_4;
        den = Sd_2 + Sd_4;
        apx->u1[l] = apx->u1[l] - num / den;

        *mx_diff = MAX(*mx_diff, fabs(old_u1 - apx->u1[l]));
    }



    /* Last point */
    l = np-1;

    old_u1 = apx->u1[l];
    S_2=0.;
    S_4=0.;
    Sd_2=0.;
    Sd_4=0.;

    for (m = 0; m <= 1; m++)
    {
        tc_i=m;
        tc_j=TC_j[m];

        u1_f11dd = apx->u1[l+(-m)] * sfi->f11dd[tc_j];
        u2_f12dd = apx->u2[l+(-m)] * sfi->f12dd[tc_i];
        u1_f11 = apx->u1[l+(-m)] * sfi->f11[tc_j];
        u2_f12 = apx->u2[l+(-m)] * sfi->f12[tc_i];
        g_pf1 = g_in[l+(-m)] * sfi->pf1[tc_j];
        S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f11dd + u2_f12dd) + 2. * (u1_f11 + u2_f12 - g_pf1);
    }

    c = 0;
    Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f11dd[c] + 2. * sfi->f11[c];

    /* In the following, TC is used because the order is relevant */
    for (m = 0; m <= 7; m++)
    {
        tc_h=TC.h[m];
        tc_k=TC.k[m];

        s_s_u1_ppf11dd = apx->s[l+pos.i[tc_k]-pos.k[tc_k]] * apx->s[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf11dd[tc_k];
        s_s_u2_ppf12dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf12dd[tc_h];
        sgm_sgm_u1_ppf11d = apx->sgm[l+pos.i[tc_k]-pos.k[tc_k]] * apx->sgm[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf11d[tc_k];
        sgm_sgm_u2_ppf12d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf12d[tc_h];
        S_4 += 2. * prm.gamma * (s_s_u1_ppf11dd + s_s_u2_ppf12dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf11d + sgm_sgm_u2_ppf12d);
    }

    /* In the following cases, pos.h[] == pos.k[] since the running combinations are those with h=k=l (i is not equal to l)
     * Only the central part of the combination sequencies (m=5 ... 11) is hence considered.
     * For this set of combinations: TC.h[m] == TC.k[m] --- For simplicity, only the index h is used
     * Since we are now considering the last point, the central part of the combination sequencies reduces to m=5 ... 7 */
    for (m = 5; m <= 7; m++) /// *here m is a counter and no longer the combinations id which is given by TC* /
    {
        tc_h=TC.h[m];
        s_s_ppf11dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11dd[tc_h];
        sgm_sgm_ppf11d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf11d[tc_h];
        Sd_4 += 2. * prm.gamma * s_s_ppf11dd + 2. * prm.mu_eps * sgm_sgm_ppf11d;
    }

    /* Here c is the combinations index (TC.x[0] is equal to 0 for every x, with x=i,j,h,k) */
    c = 0;
    s_s_ppf11dd = apx->s[l+pos.i[c]-pos.h[c]] * apx->s[l+pos.j[c]-pos.h[c]] * sfi->ppf11dd[c];
    sgm_sgm_ppf11d = apx->sgm[l+pos.j[c]-pos.h[c]] * apx->sgm[l+pos.j[c]-pos.h[c]] * sfi->ppf11d[c];
    Sd_4 += 2. * prm.gamma * s_s_ppf11dd + 2. * prm.mu_eps * sgm_sgm_ppf11d;

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    apx->u1[l] = apx->u1[l] - num / den;

    *mx_diff = MAX(*mx_diff, fabs(old_u1 - apx->u1[l]));


    return (0);
}



/* ========================================================================= */
/* Minimization of the functional's function u' */
/* ========================================================================= */
int minimize_u2(double *g_in ,int np, func_params prm, appx_u_s_sigma *apx, shp_fun_int *sfi, pos_idx_jhk pos, combs TC, int *TC_j)
{
    int l;
    double num=0., den=1.;

    int c, m, tc_i, tc_j, tc_h, tc_k;
    double S_2=0., S_4=0.;
    double Sd_2=0., Sd_4=0.;

    double u1_f12dd=0., u2_f22dd=0., u1_f12=0., u2_f22=0., g_pf2=0.;
    double s_s_u1_ppf12dd=0., s_s_u2_ppf22dd=0., sgm_sgm_u1_ppf12d=0., sgm_sgm_u2_ppf22d=0.;
    double s_s_ppf22dd=0., sgm_sgm_ppf22d=0.;



    /* First point */
    l = 0;

    for (m = 3; m <= 4 ; m++)
    {
        tc_i=m;
        tc_j=TC_j[m];

        u1_f12dd = apx->u1[l-(m-4)] * sfi->f12dd[tc_j];
        u2_f22dd = apx->u2[l-(m-4)] * sfi->f22dd[tc_i];
        u1_f12 = apx->u1[l-(m-4)] * sfi->f12[tc_j];
        u2_f22 = apx->u2[l-(m-4)] * sfi->f22[tc_i];
        g_pf2 = g_in[l-(m-4)] * sfi->pf2[tc_j];
        S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f12dd + u2_f22dd) + 2. * (u1_f12 + u2_f22 - g_pf2);
    }

    c = 4;
    Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f22dd[c] + 2. * sfi->f22[c];
    for (m = 9; m <= 16; m++)
    {
        tc_h=TC.h[m];
        tc_k=TC.k[m];

        s_s_u1_ppf12dd = apx->s[l+pos.i[tc_k]-pos.k[tc_k]] * apx->s[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf12dd[tc_k];
        s_s_u2_ppf22dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf22dd[tc_h];
        sgm_sgm_u1_ppf12d = apx->sgm[l+pos.i[tc_k]-pos.k[tc_k]] * apx->sgm[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf12d[tc_k];
        sgm_sgm_u2_ppf22d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf22d[tc_h];
        S_4 += 2. * prm.gamma * (s_s_u1_ppf12dd + s_s_u2_ppf22dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf12d + sgm_sgm_u2_ppf22d);
    }

    for (m = 9; m <= 11; m++)
    {
        tc_h=TC.h[m];

        s_s_ppf22dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22dd[tc_h];
        sgm_sgm_ppf22d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22d[tc_h];
        Sd_4 += 2. * prm.gamma * s_s_ppf22dd + 2. * prm.mu_eps * sgm_sgm_ppf22d;
    }

    c = 16;
    s_s_ppf22dd = apx->s[l+pos.h[c]] * apx->s[l+pos.k[c]] * sfi->ppf22dd[c];
    sgm_sgm_ppf22d = apx->sgm[l+pos.h[c]] * apx->sgm[l+pos.k[c]] * sfi->ppf22d[c];
    Sd_4 += 2. * prm.gamma * s_s_ppf22dd + 2. * prm.mu_eps * sgm_sgm_ppf22d;

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    apx->u2[l] = apx->u2[l] - num / den;



    /* Internal points */
    for (l = 1; l <= np-2; l++)
    {
        S_2=0.;
        S_4=0.;
        Sd_2=0.;
        Sd_4=0.;

        for (c = 1; c <= 3; c++)
        {
            tc_i=c;
            tc_j=TC_j[c];

            u1_f12dd = apx->u1[l+(c-2)] * sfi->f12dd[tc_j];
            u2_f22dd = apx->u2[l+(c-2)] * sfi->f22dd[tc_i];
            u1_f12 = apx->u1[l+(c-2)] * sfi->f12[tc_j];
            u2_f22 = apx->u2[l+(c-2)] * sfi->f22[tc_i];
            g_pf2 = g_in[l+(c-2)] * sfi->pf2[tc_j];

            S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f12dd + u2_f22dd) + 2. * (u1_f12 + u2_f22 - g_pf2);
        }

        c = 2;
        Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f22dd[c] + 2. * sfi->f22[c];

        for (c = 1; c <= 15; c++)
        {
            s_s_u1_ppf12dd = apx->s[l+pos.i[c]-pos.k[c]] * apx->s[l+pos.j[c]-pos.k[c]] * apx->u1[l+pos.h[c]-pos.k[c]] * sfi->ppf12dd[c];
            s_s_u2_ppf22dd = apx->s[l+pos.i[c]-pos.h[c]] * apx->s[l+pos.j[c]-pos.h[c]] * apx->u2[l+pos.k[c]-pos.h[c]] * sfi->ppf22dd[c];
            sgm_sgm_u1_ppf12d = apx->sgm[l+pos.i[c]-pos.k[c]] * apx->sgm[l+pos.j[c]-pos.k[c]] * apx->u1[l+pos.h[c]-pos.k[c]] * sfi->ppf12d[c];
            sgm_sgm_u2_ppf22d = apx->sgm[l+pos.i[c]-pos.h[c]] * apx->sgm[l+pos.j[c]-pos.h[c]] * apx->u2[l+pos.k[c]-pos.h[c]] * sfi->ppf22d[c];

            S_4 += 2. * prm.gamma * (s_s_u1_ppf12dd + s_s_u2_ppf22dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf12d + sgm_sgm_u2_ppf22d);
        }

        for (m = 5; m <= 11; m++)
        {
            tc_h=TC.h[m];

            s_s_ppf22dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22dd[tc_h];
            sgm_sgm_ppf22d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22d[tc_h];

            Sd_4 += 2. * prm.gamma * s_s_ppf22dd + 2. * prm.mu_eps * sgm_sgm_ppf22d;
        }

        num = S_2 + S_4;
        den = Sd_2 + Sd_4;
        apx->u2[l] = apx->u2[l] - num / den;
    }



    /* Last point */
    l = np-1;

    S_2=0.;
    S_4=0.;
    Sd_2=0.;
    Sd_4=0.;

    for (m = 0; m <= 1; m++)
    {
        tc_i=m;
        tc_j=TC_j[m];

        u1_f12dd = apx->u1[l+(-m)] * sfi->f12dd[tc_j];
        u2_f22dd = apx->u2[l+(-m)] * sfi->f22dd[tc_i];
        u1_f12 = apx->u1[l+(-m)] * sfi->f12[tc_j];
        u2_f22 = apx->u2[l+(-m)] * sfi->f22[tc_i];
        g_pf2 = g_in[l+(-m)] * sfi->pf2[tc_j];
        S_2 += 2. * prm.gamma * prm.lambda_eps * (u1_f12dd + u2_f22dd) + 2. * (u1_f12 + u2_f22 - g_pf2);
    }

    c = 0;
    Sd_2 = 2. * prm.gamma * prm.lambda_eps * sfi->f22dd[c] + 2. * sfi->f22[c];

    for (m = 0; m <= 7; m++)
    {
        tc_h=TC.h[m];
        tc_k=TC.k[m];

        s_s_u1_ppf12dd = apx->s[l+pos.i[tc_k]-pos.k[tc_k]] * apx->s[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf12dd[tc_k];
        s_s_u2_ppf22dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf22dd[tc_h];
        sgm_sgm_u1_ppf12d = apx->sgm[l+pos.i[tc_k]-pos.k[tc_k]] * apx->sgm[l+pos.j[tc_k]-pos.k[tc_k]] * apx->u1[l+pos.h[tc_k]-pos.k[tc_k]] * sfi->ppf12d[tc_k];
        sgm_sgm_u2_ppf22d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * apx->u2[l+pos.k[tc_h]-pos.h[tc_h]] * sfi->ppf22d[tc_h];
        S_4 += 2. * prm.gamma * (s_s_u1_ppf12dd + s_s_u2_ppf22dd) + 2. * prm.mu_eps * (sgm_sgm_u1_ppf12d + sgm_sgm_u2_ppf22d);
    }

    for (m = 5; m <= 7; m++)
    {
        tc_h=TC.h[m];

        s_s_ppf22dd = apx->s[l+pos.i[tc_h]-pos.h[tc_h]] * apx->s[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22dd[tc_h];
        sgm_sgm_ppf22d = apx->sgm[l+pos.i[tc_h]-pos.h[tc_h]] * apx->sgm[l+pos.j[tc_h]-pos.h[tc_h]] * sfi->ppf22d[tc_h];
        Sd_4 += 2. * prm.gamma * s_s_ppf22dd + 2. * prm.mu_eps * sgm_sgm_ppf22d;
    }

    c = 0;
    s_s_ppf22dd = apx->s[l+pos.h[c]] * apx->s[l+pos.k[c]] * sfi->ppf22dd[c];
    sgm_sgm_ppf22d = apx->sgm[l+pos.h[c]] * apx->sgm[l+pos.k[c]] * sfi->ppf22d[c];
    Sd_4 += 2. * prm.gamma * s_s_ppf22dd + 2. * prm.mu_eps * sgm_sgm_ppf22d;

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    apx->u2[l] = apx->u2[l] - num / den;


    return (0);
}



/* ========================================================================= */
/* Minimization of the functional's function s */
/* ========================================================================= */
int minimize_s(double *g_in ,int np, func_params prm, appx_u_s_sigma *apx, shp_fun_int *sfi, pos_idx_jhk pos, combs TC, int *TC_j)
{
    int l;
    double num=0., den=1.;

    int c, m, tc_i, tc_j;
    double S_2=0., S_4=0.;
    double Sd_2=0., Sd_4=0.;

    double s_ppd=0., sm1_pp=0.;
    double s_u1_u1_ppf11dd=0., s_u1_u2_ppf12dd=0., s_u2_u2_ppf22dd=0.;
    double u1_u1_ppf11dd=0., u1_u2_ppf12dd=0., u2_u2_ppf22dd=0.;

    /* First point */
    l=0;

    for (m = 3; m <=4; m++)
    {
        tc_j=TC_j[m];

        s_ppd = apx->s[l-(m-4)] * sfi->ppd[tc_j];
        sm1_pp = (apx->s[l-(m-4)] - 1.) * sfi->pp[tc_j];
        S_2 += 2. * prm.beta * (prm.epsilon * s_ppd + (0.25/prm.epsilon) * sm1_pp);
    }

    c=4;
    Sd_2 = 2. * prm.beta * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

    for (m = 9; m <= 16; m++)
    {
        tc_j=TC.j[m];

        s_u1_u1_ppf11dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf11dd[tc_j];
        s_u1_u2_ppf12dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf12dd[tc_j];
        s_u2_u2_ppf22dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf22dd[tc_j];
        S_4 += 2. * prm.gamma * (s_u1_u1_ppf11dd + 2. * s_u1_u2_ppf12dd + s_u2_u2_ppf22dd);
    }

    for (m = 9; m <= 11; m++)
    {
        tc_i=m;

        u1_u1_ppf11dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11dd[tc_i];
        u1_u2_ppf12dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12dd[tc_i];
        u2_u2_ppf22dd = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22dd[tc_i];
        Sd_4 += 2. * prm.gamma * (u1_u1_ppf11dd + 2. * u1_u2_ppf12dd + u2_u2_ppf22dd);
    }

    c=16;
    u1_u1_ppf11dd = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u1[l+pos.k[c]-pos.i[c]] * sfi->ppf11dd[c];
    u1_u2_ppf12dd = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf12dd[c];
    u2_u2_ppf22dd = apx->u2[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf22dd[c];
    Sd_4 += 2. * prm.gamma * (u1_u1_ppf11dd + 2. * u1_u2_ppf12dd + u2_u2_ppf22dd);

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    /**/
    if (den == 0.)
        den=1.;
    /**/
    apx->s[l] = apx->s[l] - num / den;



    /* Internal points */
    for (l = 1; l <= np-2; l++)
    {
        S_2=0.;
        S_4=0.;
        Sd_2=0.;
        Sd_4=0.;

        for (c = 1; c <= 3; c++)
        {
            s_ppd = apx->s[l-(c-2)] * sfi->ppd[c];
            sm1_pp = (apx->s[l-(c-2)] - 1.) * sfi->pp[c];

            S_2 += 2. * prm.beta * (prm.epsilon * s_ppd + (0.25/prm.epsilon) * sm1_pp);
        }

        c = 2;
        Sd_2 = 2. * prm.beta * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

        for (c = 1; c <= 15; c++)
        {
            s_u1_u1_ppf11dd = apx->s[l+pos.i[c]-pos.j[c]] * apx->u1[l+pos.h[c]-pos.j[c]] * apx->u1[l+pos.k[c]-pos.j[c]] * sfi->ppf11dd[c]; /*gamma*/
            s_u1_u2_ppf12dd = apx->s[l+pos.i[c]-pos.j[c]] * apx->u1[l+pos.h[c]-pos.j[c]] * apx->u2[l+pos.k[c]-pos.j[c]] * sfi->ppf12dd[c]; /*gamma*/
            s_u2_u2_ppf22dd = apx->s[l+pos.i[c]-pos.j[c]] * apx->u2[l+pos.h[c]-pos.j[c]] * apx->u2[l+pos.k[c]-pos.j[c]] * sfi->ppf22dd[c]; /*gamma*/

            S_4 += 2. * prm.gamma * (s_u1_u1_ppf11dd + 2. * s_u1_u2_ppf12dd + s_u2_u2_ppf22dd);
        }

        for (m = 5; m <= 11; m++)
        {
        tc_i=m;

            u1_u1_ppf11dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11dd[tc_i]; /*gamma*/
            u1_u2_ppf12dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12dd[tc_i]; /*gamma*/
            u2_u2_ppf22dd = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22dd[tc_i]; /*gamma*/

            Sd_4 += 2. * prm.gamma * (u1_u1_ppf11dd + 2. * u1_u2_ppf12dd + u2_u2_ppf22dd);
        }

        num = S_2 + S_4;
        den = Sd_2 + Sd_4;
        /**/
        if (den == 0.)
            den=1.;
        /**/
        apx->s[l] = apx->s[l] - num / den;
    }



    /* Last point */
    l = np-1;

    S_2=0.;
    S_4=0.;
    Sd_2=0.;
    Sd_4=0.;
    for (m = 0; m <=1; m++)
    {
        tc_j=TC_j[m];

        s_ppd = apx->s[l+(-m)] * sfi->ppd[tc_j];
        sm1_pp = (apx->s[l+(-m)] - 1.) * sfi->pp[tc_j];
        S_2 += 2. * prm.beta * (prm.epsilon * s_ppd + (0.25/prm.epsilon) * sm1_pp);
    }

    c=0;
    Sd_2 = 2. * prm.beta * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

    for (m = 0; m <= 7; m++)
    {
        tc_j=TC.j[m];

        s_u1_u1_ppf11dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf11dd[tc_j];
        s_u1_u2_ppf12dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf12dd[tc_j];
        s_u2_u2_ppf22dd = apx->s[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf22dd[tc_j];
        S_4 += 2. * prm.gamma * (s_u1_u1_ppf11dd + 2. * s_u1_u2_ppf12dd + s_u2_u2_ppf22dd);
    }

    for (m = 5; m <= 7; m++)
    {
        tc_i=m;

        u1_u1_ppf11dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11dd[tc_i];
        u1_u2_ppf12dd = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12dd[tc_i];
        u2_u2_ppf22dd = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22dd[tc_i];
        Sd_4 += 2. * prm.gamma * (u1_u1_ppf11dd + 2. * u1_u2_ppf12dd + u2_u2_ppf22dd);
    }

    c=0;
    u1_u1_ppf11dd = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u1[l+pos.k[c]-pos.i[c]] * sfi->ppf11dd[c];
    u1_u2_ppf12dd = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf12dd[c];
    u2_u2_ppf22dd = apx->u2[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf22dd[c];
    Sd_4 += 2. * prm.gamma * (u1_u1_ppf11dd + 2. * u1_u2_ppf12dd + u2_u2_ppf22dd);

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    /**/
    if (den == 0.)
        den=1.;
    /**/
    apx->s[l] = apx->s[l] - num / den;


    return (0);
}


/* ========================================================================= */
/* Minimization of the functional's function sigma */
/* ========================================================================= */
int minimize_sgm(double *g_in ,int np, func_params prm, appx_u_s_sigma *apx, shp_fun_int *sfi, pos_idx_jhk pos, combs TC, int *TC_j)
{
    int l;
    double num=0., den=1.;

    int c, m , tc_i, tc_j;
    double S_2=0., S_4=0.;
    double Sd_2=0., Sd_4=0.;

    double sgm_ppd=0., sgmm1_pp=0.;
    double sgm_u1_u1_ppf11d=0., sgm_u1_u2_ppf12d=0., sgm_u2_u2_ppf22d=0.;
    double u1_u1_ppf11d=0., u1_u2_ppf12d=0., u2_u2_ppf22d=0.;



    /* First point */
    l = 0;

    for (m = 3; m <= 4 ; m++)
    {
        tc_j=TC_j[m];

        sgm_ppd = apx->sgm[l-(m-4)] * sfi->ppd[tc_j];
        sgmm1_pp = (apx->sgm[l-(m-4)] - 1) * sfi->pp[tc_j];
        S_2 += 2. * (prm.alpha - prm.beta) * (prm.epsilon * sgm_ppd + (0.25/prm.epsilon) * sgmm1_pp);
    }

    c = 4;
    Sd_2 = 2. * (prm.alpha - prm.beta) * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

    for (m = 9; m <= 16; m++)
    {
        tc_j=TC.j[m];

        sgm_u1_u1_ppf11d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf11d[tc_j];
        sgm_u1_u2_ppf12d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf12d[tc_j];
        sgm_u2_u2_ppf22d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf22d[tc_j];
        S_4 += 2. * prm.mu_eps * (sgm_u1_u1_ppf11d + 2. * sgm_u1_u2_ppf12d + sgm_u2_u2_ppf22d);
    }

    for (m = 9; m <= 11; m++)
    {
        tc_i=m;

        u1_u1_ppf11d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11d[tc_i];
        u1_u2_ppf12d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12d[tc_i];
        u2_u2_ppf22d = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22d[tc_i];
        Sd_4 += 2. * prm.mu_eps * (u1_u1_ppf11d + 2. * u1_u2_ppf12d + u2_u2_ppf22d);
    }

    c=16;
    u1_u1_ppf11d = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u1[l+pos.k[c]-pos.i[c]] * sfi->ppf11d[c];
    u1_u2_ppf12d = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf12d[c];
    u2_u2_ppf22d = apx->u2[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf22d[c];
    Sd_4 += 2. * prm.mu_eps * (u1_u1_ppf11d + 2. * u1_u2_ppf12d + u2_u2_ppf22d);

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    /**/
    if (den == 0.)
        den=1.;
    /**/
    apx->sgm[l] = apx->sgm[l] - num / den;



    /* Internal points */
    for (l = 1; l <= np-2; l++)
    {
        S_2=0.;
        S_4=0.;
        Sd_2=0.;
        Sd_4=0.;

        for (c =1; c <= 3; c++)
        {
            sgm_ppd = apx->sgm[l-(c-2)] * sfi->ppd[c]; /// *(alpha-beta) * epsilon* /
            sgmm1_pp = (apx->sgm[l-(c-2)] - 1) * sfi->pp[c]; /// *(alpha-beta) / (2 * epsilon)* /

            S_2 += 2. * (prm.alpha - prm.beta) * (prm.epsilon * sgm_ppd + (0.25/prm.epsilon) * sgmm1_pp);
        }

        c = 2;
        Sd_2 = 2. * (prm.alpha - prm.beta) * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

        for (c = 1; c <= 15; c++)
        {
            sgm_u1_u1_ppf11d = apx->sgm[l+pos.i[c]-pos.j[c]] * apx->u1[l+pos.h[c]-pos.j[c]] * apx->u1[l+pos.k[c]-pos.j[c]] * sfi->ppf11d[c]; /*mu_epsilon*/
            sgm_u1_u2_ppf12d = apx->sgm[l+pos.i[c]-pos.j[c]] * apx->u1[l+pos.h[c]-pos.j[c]] * apx->u2[l+pos.k[c]-pos.j[c]] * sfi->ppf12d[c]; /*mu_epsilon*/
            sgm_u2_u2_ppf22d = apx->sgm[l+pos.i[c]-pos.j[c]] * apx->u2[l+pos.h[c]-pos.j[c]] * apx->u2[l+pos.k[c]-pos.j[c]] * sfi->ppf22d[c]; /*mu_epsilon*/

            S_4 += 2. * prm.mu_eps * (sgm_u1_u1_ppf11d + 2. * sgm_u1_u2_ppf12d + sgm_u2_u2_ppf22d);
        }

        for (m = 5; m <= 11; m++)
        {
            tc_i=m;

            u1_u1_ppf11d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11d[tc_i]; /*mu_epsilon*/
            u1_u2_ppf12d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12d[tc_i]; /*mu_epsilon*/
            u2_u2_ppf22d = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22d[tc_i]; /*mu_epsilon*/

            Sd_4 += 2. * prm.mu_eps * (u1_u1_ppf11d + 2. * u1_u2_ppf12d + u2_u2_ppf22d);
        }

        num = S_2 + S_4;
        den = Sd_2 + Sd_4;
        /**/
        if (den == 0.)
            den=1.;
        /**/
        apx->sgm[l] = apx->sgm[l] - num / den;
    }



    /* Last point*/
    l = np-1;

    S_2=0.;
    S_4=0.;
    Sd_2=0.;
    Sd_4=0.;

    for (m = 0; m <= 1; m++)
    {
        tc_j=TC_j[m];

        sgm_ppd = apx->sgm[l+(-m)] * sfi->ppd[tc_j];
        sgmm1_pp = (apx->sgm[l+(-m)] - 1) * sfi->pp[tc_j];
        S_2 += 2. * (prm.alpha - prm.beta) * (prm.epsilon * sgm_ppd + (0.25/prm.epsilon) * sgmm1_pp);
    }

    c = 0;
    Sd_2 = 2. * (prm.alpha - prm.beta) * (prm.epsilon * sfi->ppd[c] + (0.25/prm.epsilon) * sfi->pp[c]);

    for (m = 0; m <= 7; m++)
    {
        tc_j=TC.j[m];

        sgm_u1_u1_ppf11d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf11d[tc_j];
        sgm_u1_u2_ppf12d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u1[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf12d[tc_j];
        sgm_u2_u2_ppf22d = apx->sgm[l+pos.i[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.h[tc_j]-pos.j[tc_j]] * apx->u2[l+pos.k[tc_j]-pos.j[tc_j]] * sfi->ppf22d[tc_j];
        S_4 += 2. * prm.mu_eps * (sgm_u1_u1_ppf11d + 2. * sgm_u1_u2_ppf12d + sgm_u2_u2_ppf22d);
    }

    for (m = 5; m <= 7; m++)
    {
        tc_i=m;

        u1_u1_ppf11d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u1[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf11d[tc_i];
        u1_u2_ppf12d = apx->u1[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf12d[tc_i];
        u2_u2_ppf22d = apx->u2[l+pos.h[tc_i]-pos.i[tc_i]] * apx->u2[l+pos.k[tc_i]-pos.i[tc_i]] * sfi->ppf22d[tc_i];
        Sd_4 += 2. * prm.mu_eps * (u1_u1_ppf11d + 2. * u1_u2_ppf12d + u2_u2_ppf22d);
    }

    c=0;
    u1_u1_ppf11d = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u1[l+pos.k[c]-pos.i[c]] * sfi->ppf11d[c];
    u1_u2_ppf12d = apx->u1[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf12d[c];
    u2_u2_ppf22d = apx->u2[l+pos.h[c]-pos.i[c]] * apx->u2[l+pos.k[c]-pos.i[c]] * sfi->ppf22d[c];
    Sd_4 += 2. * prm.mu_eps * (u1_u1_ppf11d + 2. * u1_u2_ppf12d + u2_u2_ppf22d);

    num = S_2 + S_4;
    den = Sd_2 + Sd_4;
    /**/
    if (den == 0.)
        den=1.;
    /**/
    apx->sgm[l] = apx->sgm[l] - num / den;


    return (0);
}
